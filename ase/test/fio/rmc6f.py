import os
import numpy as np
from ase import Atoms, io


rmc6f_input_text = """
(Version 6f format configuration file)
Metadata owner:     Joe Smith
Metadata date:      31-01-1900
Metadata material:  SF6
Metadata comment:  Some comments go here...
Metadata source:    GSAS
Number of moves generated:           89692
Number of moves tried:               85650
Number of moves accepted:            10074
Number of prior configuration saves: 0
Number of atoms:                     7
Number density (Ang^-3):                 0.068606
Supercell dimensions:                1 1 1
Cell (Ang/deg): 4.672816 4.672816 4.672816 90.0 90.0 90.0
Lattice vectors (Ang):
    4.672816    0.000000    0.000000
    0.000000    4.672816    0.000000
    0.000000    0.000000    4.672816
Atoms:
     1   S     0.600452    0.525100    0.442050     1   0   0   0
     2   F     0.911952    0.450722    0.382733     2   0   0   0
     3   F     0.283794    0.616712    0.500094     3   0   0   0
     4   F     0.679823    0.854839    0.343915     4   0   0   0
     5   F     0.531660    0.229024    0.535688     5   0   0   0
     6   F     0.692514    0.584931    0.746683     6   0   0   0
     7   F     0.509687    0.449350    0.111960     7   0   0   0
"""

symbols = ['S', 'F', 'F', 'F', 'F', 'F', 'F']
lat = 4.672816
positions = lat * np.array([
    [0.600452, 0.525100, 0.442050],
    [0.911952, 0.450722, 0.382733],
    [0.283794, 0.616712, 0.500094],
    [0.679823, 0.854839, 0.343915],
    [0.531660, 0.229024, 0.535688],
    [0.692514, 0.584931, 0.746683],
    [0.509687, 0.449350, 0.111960]])
cell = [lat, lat, lat]
rmc6f_atoms = Atoms(symbols, positions=positions, cell=cell, pbc=[1, 1, 1])


def test_rmc6f_read():
    """Test for reading rmc6f input file."""
    with open('input.rmc6f', 'w') as rmc6f_input_f:
        rmc6f_input_f.write(rmc6f_input_text)

    try:
        rmc6f_input_atoms = io.read('input.rmc6f')
        assert len(rmc6f_input_atoms) == 7
        assert rmc6f_input_atoms == rmc6f_atoms
    finally:
        os.unlink('input.rmc6f')


def test_rmc6f_write():
    """Test for writing rmc6f input file."""
    try:
        io.write('output.rmc6f', rmc6f_atoms)
        readback = io.read('output.rmc6f')
        assert np.allclose(rmc6f_atoms.positions, readback.positions)
        assert readback == rmc6f_atoms
    finally:
        os.unlink('output.rmc6f')


def test_rmc6f_read_construct_regex():
    """Test for utility function that constructs rmc6f header regex."""
    header_lines = [
        "Number of atoms:",
        "  Supercell dimensions:  ",
        "    Cell (Ang/deg):  ",
        "      Lattice vectors (Ang):  "]
    result = io.rmc6f._read_construct_regex(header_lines)
    target = "(Number\\s+of\\s+atoms:|Supercell\\s+dimensions:|Cell\\s+\\(Ang/deg\\):|Lattice\\s+vectors\\s+\\(Ang\\):)"  # noqa: E501
    assert result == target


def test_rmc6f_read_line_of_atoms_section_style_no_labels():
    """Test for reading a line of atoms section
    w/ 'no labels' style for rmc6f
    """
    atom_line = "1 S 0.600452 0.525100 0.442050 1 0 0 0"
    atom_id, props = io.rmc6f._read_line_of_atoms_section(atom_line.split())
    target_id = 1
    target_props = ['S', 0.600452, 0.5251, 0.44205]
    assert atom_id == target_id
    assert props == target_props


def test_rmc6f_read_line_of_atoms_section_style_labels():
    """Test for reading a line of atoms section
    w/ 'labels'-included style for rmc6f
    """
    atom_line = "1 S [1] 0.600452 0.525100 0.442050 1 0 0 0"
    atom_id, props = io.rmc6f._read_line_of_atoms_section(atom_line.split())
    target_id = 1
    target_props = ['S', 0.600452, 0.5251, 0.44205]
    assert atom_id == target_id
    assert props == target_props


def test_rmc6f_read_line_of_atoms_section_style_magnetic():
    """Test for reading a line of atoms section
    w/ 'magnetic' style for rmc6f
    """
    atom_line = "1 S 0.600452 0.525100 0.442050 1 0 0 0 M: 0.1"
    atom_id, props = io.rmc6f._read_line_of_atoms_section(atom_line.split())
    target_id = 1
    target_props = ['S', 0.600452, 0.5251, 0.44205, 0.1]
    assert atom_id == target_id
    assert props == target_props


def test_rmc6f_read_process_rmc6f_lines_to_pos_and_cell():
    """Test for utility function that processes lines of rmc6f using
    regular expressions to capture atom properties and cell information
    """
    lines = rmc6f_input_text.split('\n')
    props, cell = io.rmc6f._read_process_rmc6f_lines_to_pos_and_cell(lines)

    target_props = {
        1: ['S', 0.600452, 0.5251, 0.44205],
        2: ['F', 0.911952, 0.450722, 0.382733],
        3: ['F', 0.283794, 0.616712, 0.500094],
        4: ['F', 0.679823, 0.854839, 0.343915],
        5: ['F', 0.53166, 0.229024, 0.535688],
        6: ['F', 0.692514, 0.584931, 0.746683],
        7: ['F', 0.509687, 0.44935, 0.11196]}

    target_cell = np.zeros((3, 3), float)
    np.fill_diagonal(target_cell, 4.672816)

    assert props == target_props
    assert np.array_equal(cell, target_cell)


def test_rmc6f_read_process_rmc6f_lines_to_pos_and_cell_padded_whitespace():
    """Test for utility function that processes lines of rmc6f using
    regular expressions to capture atom properties and cell information
    with puposeful whitespace padded on one line
    """
    lines = rmc6f_input_text.split('\n')
    lines[14] = "    {}    ".format(lines[14])  # intentional whitespace
    props, cell = io.rmc6f._read_process_rmc6f_lines_to_pos_and_cell(lines)

    target_props = {
        1: ['S', 0.600452, 0.5251, 0.44205],
        2: ['F', 0.911952, 0.450722, 0.382733],
        3: ['F', 0.283794, 0.616712, 0.500094],
        4: ['F', 0.679823, 0.854839, 0.343915],
        5: ['F', 0.53166, 0.229024, 0.535688],
        6: ['F', 0.692514, 0.584931, 0.746683],
        7: ['F', 0.509687, 0.44935, 0.11196]}

    target_cell = np.zeros((3, 3), float)
    np.fill_diagonal(target_cell, 4.672816)

    assert props == target_props
    assert np.array_equal(cell, target_cell)


def test_rmc6f_write_output_column_format():
    """Test for utility function that processes the columns in array
    and gets back out formatting information.
    """
    cols = ['id', 'symbols', 'scaled_positions', 'ref_num', 'ref_cell']
    arrays = {}
    arrays['id'] = np.array([1, 2, 3, 4, 5, 6, 7])
    arrays['symbols'] = np.array(symbols)
    arrays['ref_num'] = np.zeros(7, int)
    arrays['ref_cell'] = np.zeros((7, 3), int)
    arrays['scaled_positions'] = positions / lat

    ncols, dtype_obj, fmt = io.rmc6f._write_output_column_format(cols, arrays)

    target_ncols = [1, 1, 3, 1, 3]
    target_dtype_obj = [
        ('id', '<i8'),
        ('symbols', '<U1'), ('scaled_positions0', '<f8'),
        ('scaled_positions1', '<f8'),
        ('scaled_positions2', '<f8'),
        ('ref_num', '<i8'),
        ('ref_cell0', '<i8'),
        ('ref_cell1', '<i8'),
        ('ref_cell2', '<i8')]
    target_fmt = "%8d %s%14.6f %14.6f %14.6f %8d %8d %8d %8d \n"

    assert ncols == target_ncols
    assert dtype_obj == target_dtype_obj
    assert fmt == target_fmt


def test_rmc6f_write_output():
    """Test for utility function for writing rmc6f output
    """
    fileobj = "output.rmc6f"
    header_lines = [
        '(Version 6f format configuration file)',
        '(Generated by ASE - Atomic Simulation Environment https://wiki.fysik.dtu.dk/ase/ )',  # noqa: E501
        "Metadata date:18-007-'2019",
        'Number of types of atoms:   2 ',
        'Atom types present:          S F',
        'Number of each atom type:   1 6',
        'Number of moves generated:           0',
        'Number of moves tried:               0',
        'Number of moves accepted:            0',
        'Number of prior configuration saves: 0',
        'Number of atoms:                     7',
        'Supercell dimensions:                1 1 1',
        'Number density (Ang^-3):              0.06860598423060468',
        'Cell (Ang/deg): 4.672816 4.672816 4.672816 90.0 90.0 90.0',
        'Lattice vectors (Ang):',
        '    4.672816     0.000000     0.000000',
        '    0.000000     4.672816     0.000000',
        '    0.000000     0.000000     4.672816',
        'Atoms:']
    data_array = [
        (1, 'S', 0.600452, 0.5251, 0.44205, 0, 0, 0, 0),
        (2, 'F', 0.911952, 0.450722, 0.382733, 0, 0, 0, 0),
        (3, 'F', 0.283794, 0.616712, 0.500094, 0, 0, 0, 0),
        (4, 'F', 0.679823, 0.854839, 0.343915, 0, 0, 0, 0),
        (5, 'F', 0.53166, 0.229024, 0.535688, 0, 0, 0, 0),
        (6, 'F', 0.692514, 0.584931, 0.746683, 0, 0, 0, 0),
        (7, 'F', 0.509687, 0.44935, 0.11196, 0, 0, 0, 0)]
    data_dtype = [
        ('id', '<i8'),
        ('symbols', '<U1'),
        ('scaled_positions0', '<f8'),
        ('scaled_positions1', '<f8'),
        ('scaled_positions2', '<f8'),
        ('ref_num', '<i8'),
        ('ref_cell0', '<i8'),
        ('ref_cell1', '<i8'),
        ('ref_cell2', '<i8')]
    data = np.array(data_array, dtype=data_dtype)
    fmt = "%8d %s%14.6f %14.6f %14.6f %8d %8d %8d %8d \n"
    with open('output.rmc6f', 'w') as fileobj:
        io.rmc6f._write_output(fileobj, header_lines, data, fmt)


def test_write_rmc_get_cell_from_cellpar():
    """Test for utility function converts cell parameters to cell
    """
    cellpar = [4.672816, 4.672816, 4.672816, 90.0, 90.0, 90.0]
    cell = io.rmc6f._write_rmc_get_cell_from_cellpar(cellpar)
    target_cell = np.zeros((3, 3), float)
    np.fill_diagonal(target_cell, 4.672816)
    assert np.array_equal(cell, target_cell)


# Tests
test_rmc6f_read()
test_rmc6f_write()
test_rmc6f_read_construct_regex()
test_rmc6f_read_line_of_atoms_section_style_no_labels()
test_rmc6f_read_line_of_atoms_section_style_labels()
test_rmc6f_read_line_of_atoms_section_style_magnetic()
test_rmc6f_read_process_rmc6f_lines_to_pos_and_cell()
test_rmc6f_read_process_rmc6f_lines_to_pos_and_cell_padded_whitespace()
test_rmc6f_write_output_column_format()
test_rmc6f_write_output()
test_write_rmc_get_cell_from_cellpar()
