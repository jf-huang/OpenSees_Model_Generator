"""
Basic Tests
"""

# import pytest
import numpy as np
import numpy.typing as npt
from osmg.model import Model
from osmg.graphics.preprocessing_3d import show
from osmg import defaults
from osmg.gen.section_gen import SectionGenerator
from osmg.ops.section import ElasticSection
from osmg.gen.component_gen import BeamColumnGenerator
from osmg.ops.element import ElasticBeamColumn
from osmg.load_case import LoadCase
from osmg.gen.query import ElmQuery
from osmg.preprocessing.self_weight_mass import self_weight
from osmg.preprocessing.self_weight_mass import self_mass
from osmg.solver import PushoverAnalysis
from osmg.graphics.postprocessing_3d import show_deformed_shape
from osmg.graphics.postprocessing_3d import show_basic_forces
from osmg.gen.zerolength_gen import gravity_shear_tab


nparr = npt.NDArray[np.float64]


def test_a():
    """
    Basic functionality tests
    Simple frame model
    Imperial units
    """

    mdl = Model('test_model')
    mdl.settings.imperial_units = True

    mcg = BeamColumnGenerator(mdl)
    secg = SectionGenerator(mdl)
    query = ElmQuery(mdl)

    mdl.add_level(0, 0.00)
    mdl.add_level(1, 15.00 * 12.00)

    defaults.load_default_steel(mdl)
    defaults.load_default_fix_release(mdl)
    steel_phys_mat = mdl.physical_materials.retrieve_by_attr(
        'name', 'default steel')

    section_type = ElasticSection
    element_type = ElasticBeamColumn
    sec_collection = mdl.elastic_sections

    mdl.levels.set_active([1])

    secg.load_aisc_from_database(
        'W',
        ['W24X131'],
        'default steel',
        'default steel',
        section_type
    )

    pt0: nparr = np.array((0.00, 0.00))
    pt1: nparr = np.array((0.00, 25.00 * 12.00))

    sec = sec_collection.retrieve_by_attr('name', 'W24X131')

    mcg.add_vertical_active(
        pt0[0], pt0[1],
        np.zeros(3), np.zeros(3),
        'Linear',
        1,
        sec,
        element_type,
        'centroid',
        2.00 * np.pi / 2.00
    )

    mcg.add_vertical_active(
        pt1[0], pt1[1],
        np.zeros(3), np.zeros(3),
        'Linear',
        1,
        sec,
        element_type,
        'centroid',
        2.00 * np.pi / 2.00
    )

    mcg.add_horizontal_active(
        pt0[0], pt0[1],
        pt1[0], pt1[1],
        np.array((0., 0., 0.)),
        np.array((0., 0., 0.)),
        'bottom_center',
        'top_center',
        'Linear',
        1,
        sec,
        element_type,
        'top_center',
        method='generate_hinged_component_assembly',
        additional_args={
            'zerolength_gen_i': gravity_shear_tab,
            'zerolength_gen_args_i': {
                'consider_composite': True,
                'section': sec,
                'physical_material': steel_phys_mat,
                'distance': 10.00,
                'n_sub': 1
            },
            'zerolength_gen_j': gravity_shear_tab,
            'zerolength_gen_args_j': {
                'consider_composite': True,
                'section': sec,
                'physical_material': steel_phys_mat,
                'distance': 10.00,
                'n_sub': 1
            }
        }
    )

    # fix base
    for node in mdl.levels[0].nodes.values():
        node.restraint = [True]*6

    testcase = LoadCase('test', mdl)
    self_weight(mdl, testcase)
    self_mass(mdl, testcase)

    show(mdl, testcase)

    control_node = query.search_node_lvl(0.00, 0.00, 1)

    anl = PushoverAnalysis(mdl, {testcase.name: testcase})

    anl.run('y', [+50.00], control_node, 0.1, loaded_node=control_node)

    show_deformed_shape(
        anl, testcase.name,
        anl.results[testcase.name].n_steps_success,
        0.00, True, animation=False)

    show_basic_forces(anl, testcase.name, 0, 1.00, 0.00, 0.00, 0.00, 0.00, 3)

    # zelms = mdl.list_of_zerolength_elements()
    # zelm = zelms[0].uid
    # res_a = anl.retrieve_release_force_defo(zelm, testcase.name)

    anl.run('y', [-50.00], control_node, 0.1, loaded_node=control_node)

    # deformed_shape(anl, anl.n_steps_success, 0.00, True)
    # res_b = anl.retrieve_release_force_defo(zelm, testcase.name)


if __name__ == '__main__':
    pass
