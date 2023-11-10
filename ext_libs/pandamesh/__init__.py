import pkg_resources

from pandamesh import data
from pandamesh.gmsh_mesher import (
    FieldCombination,
    GmshMesher,
    MeshAlgorithm,
    SubdivisionAlgorithm,
    gmsh_env,
)
from pandamesh.plot import plot
from pandamesh.triangle_mesher import DelaunayAlgorithm, TriangleMesher
from pandamesh import common
from pandamesh import gmsh_geometry

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    # package is not installed
    pass
