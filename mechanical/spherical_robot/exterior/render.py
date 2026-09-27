"""Orthographic engineering views from the exact exported STL triangles."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'exports/exterior'


def main():
  receipt = json.loads((OUT/'verification.json').read_text())
  fig = plt.figure(figsize=(14,10),facecolor='#f5f6f8')
  views = [(0,0,'Outside'),(15,85,'Edge'),(25,35,'Three-quarter')]
  for row, item in enumerate(receipt['parts']):
    mesh = trimesh.load_mesh(OUT/(item['part']+'.stl'))
    for col,(elev,azim,label) in enumerate(views):
      ax=fig.add_subplot(3,3,row*3+col+1,projection='3d',proj_type='ortho')
      poly=Poly3DCollection(mesh.triangles,facecolor='#92aec6',edgecolor='#41586c',linewidth=0.04)
      ax.add_collection3d(poly)
      ax.set_xlim(85,155);ax.set_ylim(-55,55);ax.set_zlim(-35,35)
      ax.set_box_aspect((70,110,70));ax.view_init(elev=elev,azim=azim)
      ax.set_axis_off();ax.set_title(item['part']+'\n'+label,fontsize=9)
  fig.suptitle('P0.3 exterior candidate — exact STL geometry\nMesh verified; full assembly, slicing and physical fit pending',fontsize=14)
  fig.tight_layout(rect=[0,0,1,0.94])
  fig.savefig(OUT/'geometry-review.png',dpi=140)
  plt.close(fig)


if __name__ == '__main__':
  main()
