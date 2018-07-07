File content description table:


__init__.py         # Contains register functions and bl_info data

build_data.py       # Contains build data access functions

builder.py          # Contains constraints builder function

builder_fm.py       # Contains constraints builder function for Fracture Modifier (custom Blender version required)

builder_prep.py     # Contains preparation steps functions called by the builder

builder_setc.py     # Contains constraints settings functions called by the builder

file_io.py          # Contains file input & output functions

formula.py          # Contains formula assistant functions

formula_props.py    # Contains formula assistant properties classes

global_props.py     # Contains global properties

global_vars.py      # Contains global variables

gui.py              # Contains graphical user interface layout class

gui_buttons.py      # Contains graphical user interface button classes

monitor.py          # Contains baking monitor event handler

tools.py            # Contains smaller independently working tools


/extern/                              # External modules (independently developed)

kk_import_motion_from_text_file.py    # Contains earthquake motion import function

kk_mesh_fracture.py                   # Contains boolean based discretization function

kk_mesh_separate_less_loose.py        # Contains polygon based discretization function for non-manifolds

kk_mesh_separate_loose.py             # Contains speed-optimized mesh island separation function

kk_mesh_subdiv_to_level.py            # Contains edge length based subdivision function for non-manifolds

kk_mesh_voxel_cell_grid_from_mesh.py  # Contains voxel based discretization function

kk_select_intersecting_objects.py     # Contains intersection detection and resolving function
