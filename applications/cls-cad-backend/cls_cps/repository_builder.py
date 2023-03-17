import json
from enum import Enum
from functools import reduce

from bcls import Arrow, Constructor, Omega, Subtypes, Type

from cls_cps.cls_python.cls_json import CLSEncoder
from cls_cps.database.commands import get_all_parts_for_project
from cls_cps.util.motion import combine_motions


class Part:
    def __call__(self, *required_parts):
        return dict(
            self.info,
            count=1,
            connections={
                uuid: dict(
                    required_part()
                    if isinstance(required_part, Part)
                    else required_part,
                    count=uuid_info["count"],
                    motion=combine_motions(self.info["motion"], uuid_info["motion"]),
                )
                for (uuid, uuid_info), required_part in zip(
                    self.info["requiredJointOriginsInfo"].items(), required_parts
                )
            },
        )

    def __repr__(self):
        return self.__call__()

    def __str__(self):
        return ""

    def __hash__(self):
        return hash(json.dumps(self.info))

    def __init__(self, info):
        # Create combinator type here based on some JSON payload in future
        self.info = info

    def __eq__(self, other):
        return isinstance(other, Part) and self.__hash__() == other.__hash__()


class Role(str, Enum):
    requires = "requires"
    provides = "provides"


def get_joint_origin_type(uuid: str, part: dict, role: Role):
    return Type.intersect(
        [Constructor(tpe) for tpe in part["jointOrigins"][uuid][role]]
    )


def is_blacklisted_under_subtyping(
    blacklist, joint_origin_uuid, part, taxonomy, role: Role
):
    return bool(blacklist) and taxonomy.check_subtype(
        get_joint_origin_type(joint_origin_uuid, part, role),
        Type.intersect([Constructor(t) for t in blacklist]),
    )


def fetch_required_joint_origins_info(part, configuration):
    return {
        joint_origin_uuid: fetch_joint_origin_info(part, joint_origin_uuid)
        for joint_origin_uuid in configuration["requiresJointOrigins"]
    }


def fetch_joint_origin_info(part, joint_origin_uuid: str):
    return part["jointOrigins"][joint_origin_uuid]


def create_virtual_substitute_part(part, required_joint_origin_uuid):
    return Part(
        {
            "name": "clsconnectmarker_"
            + str(
                hash(
                    json.dumps(
                        get_joint_origin_type(
                            required_joint_origin_uuid, part, Role.requires
                        ),
                        cls=CLSEncoder,
                    )
                )
            ),
            "forgeDocumentId": "NoInsert",
            "forgeFolderId": "NoInsert",
            "forgeProjectId": "NoInsert",
            "jointOrder": {},
            "provides": required_joint_origin_uuid,
            "motion": "Rigid",
        }
    )


def types_from_uuids(uuids: list, part: dict):
    return [
        *[get_joint_origin_type(x, part, Role.requires) for x in uuids[:-1]],
        *[get_joint_origin_type(uuids[-1], part, Role.provides)],
    ]


def multiarrow_from_types(type_list):
    return reduce(lambda a, b: Arrow(b, a), reversed(type_list))


def multiarrow_to_self(tpe, length):
    return multiarrow_from_types([tpe] * length)


def intersect_all_multiarrows_containing_type(tpe, length):
    result = []
    for x in range(0, length - 1):
        multiarrow_type_list = [Omega()] * length
        multiarrow_type_list[x] = tpe
        multiarrow_type_list[-1] = tpe
        result.append(multiarrow_from_types(multiarrow_type_list))
    return Type.intersect(result)


class RepositoryBuilder:
    @staticmethod
    def add_part_to_repository(
        part: dict,
        repository: dict,
        *,
        blacklist=None,
        connect_uuid=None,
        taxonomy: Subtypes = None,
        propagated_types=[]
    ):
        """
        Adds a part to a repository to be used for synthesis. Adds necessary Constructors for the parts configurations,
        unless the configuration provides a blacklisted type. The blacklist is intended to be used for synthesising
        connectors, since a constructor for the type and its subtypes needs to be added but all productions for that
        type and its subtypes need to be removed. This guarantees that all results that request that type terminate in
        that Constructor or subtypes of it, which then indicate the point of connection.

        If a blacklist is provided, also adds Constructors for every encountered required type that is
        more specific than the blacklist.

        :param propagated_types:
        :param part: The JSON representation of the part to add to the repository. This uses set() as its array type.
        :param repository: The repository dict for the part to be added to. This should be then used for synthesis.
        :param blacklist: An optional set that represent a Types.intersect([blacklist]).
        :param connect_uuid: The UUID of the joint the blacklist is based on.
        :param taxonomy: The taxonomy to check the blacklist with.
        :return:
        """
        for configuration in part["configurations"]:
            # Since SetDecoder is used for creating the part dict, we can just check if the part provides the leaf type
            # or an even more specific type, which we also can not allow.
            pass

            if is_blacklisted_under_subtyping(
                blacklist,
                configuration["providesJointOrigin"],
                part,
                taxonomy,
                Role.provides,
            ):
                continue

            ordered_list_of_configuration_uuids = [
                *configuration["requiresJointOrigins"],
                *[configuration["providesJointOrigin"]],
            ]

            config_types = types_from_uuids(ordered_list_of_configuration_uuids, part)
            config_multiarrow = multiarrow_from_types(config_types)

            if propagated_types:
                propagated_types_intersections = [
                    intersect_all_multiarrows_containing_type(
                        Type.intersect([Constructor(tpe) for tpe in tpe_list]),
                        len(config_types),
                    )
                    for tpe_list in propagated_types
                ]

                config_multiarrow = Type.intersect(
                    [*[config_multiarrow], *propagated_types_intersections]
                )

            repository[
                Part(
                    dict(
                        part["meta"],
                        requiredJointOriginsInfo=fetch_required_joint_origins_info(
                            part, configuration
                        ),
                        provides=configuration["providesJointOrigin"],
                        motion=fetch_joint_origin_info(
                            part, configuration["providesJointOrigin"]
                        )["motion"],
                    )
                )
            ] = config_multiarrow

            for required_joint_origin_uuid in configuration["requiresJointOrigins"]:
                # If a joint would require a blacklisted type or a subtype of it, we add that specific
                # version to the repository as a virtual Part along with a fitting PartConfig. This results in the
                # output JSON specifying that virtual part for the "back-side" of the synthesised connector.
                if not is_blacklisted_under_subtyping(
                    blacklist, required_joint_origin_uuid, part, taxonomy, Role.provides
                ):
                    continue

                repository[
                    create_virtual_substitute_part(part, required_joint_origin_uuid)
                ] = get_joint_origin_type(
                    required_joint_origin_uuid, part, Role.requires
                )

    @staticmethod
    def add_all_to_repository(
        project_id: str,
        *,
        blacklist=None,
        connect_uuid=None,
        taxonomy=None,
        propagated_types=[]
    ):
        repository = {}
        for part in get_all_parts_for_project(project_id):
            RepositoryBuilder.add_part_to_repository(
                part,
                repository,
                blacklist=blacklist,
                connect_uuid=connect_uuid,
                taxonomy=taxonomy,
                propagated_types=propagated_types,
            )
        return repository
