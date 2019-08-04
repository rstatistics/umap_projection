#! /usr/bin/python
import sys
import numpy as np
import umap
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] =42
from scipy.stats import rankdata 
import argparse
import seaborn as sns

def parser_user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('-rm','--ref-matrix',required=True,help='Path to count matrix for reference.')
    parser.add_argument('-pm','--proj-matrices',nargs='+',required=True,help='Path to count matrices for query samples.')
    parser.add_argument('-p','--prefix',required=True,help='Prefix for output including path.')
    parser.add_argument('-m','--markers',required=True,help='Path to file with one-column list of marker gids (cell-cell similarity will be computed using these markers).')
    parser.add_argument('-k','-k',required=True,default=20,type=int,help='Integer value of k parameter for UMAP.')
    return parser

# for loading molecular count matrix for a list of marker gids with format GID\tSYMBOL\tCTS_CELL1\tCTS_CELL2\t...
# first column in marker_INFILE contains list of marker gids
# if fill==1, counts will be set to zero for any marker absent from the matrix
def load_marker_matrix(matrix_INFILE,marker_INFILE,fill):
    gids = []
    genes = []
    matrix = []
    with open(marker_INFILE) as f:
        markers = set([line.split()[0] for line in f])
    with open(matrix_INFILE) as f:
        for line in f:
            llist = line.split()
            gid = llist[0]
            if gid in markers:
                gids.append(gid)
                genes.append(llist[1])
                try:
                    matrix.append([int(pt) for pt in llist[2::]])
                except ValueError:
                    matrix.append([float(pt) for pt in llist[2::]])
    if fill == 1:
        for gid in markers:
            if gid not in gids:
                gids.append(gid)
                genes.append(gid)
                matrix.append([0 for pt in range(len(matrix[0]))])
    gids = np.array(gids)
    ind = np.argsort(gids)
    gids = gids[ind]
    genes = np.array(genes)[ind]
    matrix = np.array(matrix)[ind]
    return gids, genes, matrix


parser = parser_user_input()
ui = parser.parse_args()

print('Loading data...')
rgids,rgenes,rmatrix = load_marker_matrix(ui.ref_matrix,ui.markers,1)

print('Computing model...')
ref_rank = np.apply_along_axis(rankdata,1,rmatrix)
umap_model = umap.UMAP(n_neighbors=ui.k,random_state=42,metric='correlation').fit(ref_rank.T)
umap_model_emb = umap_model.embedding_
model_output = ui.prefix+'.ref_emb.umap.txt'
np.savetxt(model_output,umap_model_emb,delimiter='\t',fmt='%f')

print('Computing projections...')
projs = []
for i,proj_matrix in enumerate(ui.proj_matrices):
    pgids,pgenes,pmatrix = load_marker_matrix(proj_matrix,ui.markers,1)
    if len(pgids) < len(rgids):
        print('Error: Some marker GIDS in the reference matrix are missing in the query matrix %(i)d.' % vars())
        exit()
    elif len(rgids) > len(pgids):
        print('Error: Some marker GIDS in query matrix %(i)d are missing from the reference matrix.' % vars())
        exit()
    prj_rank = np.apply_along_axis(rankdata,1,pmatrix)
    umap_proj = umap_model.transform(prj_rank.T)
    proj_output = ui.prefix+'.proj.'+str(i)+'.umap.txt'
    np.savetxt(proj_output,umap_proj,delimiter='\t',fmt='%f')
    projs.append(umap_proj)

print('Plotting output...')
pdf_output = ui.prefix+'.pdf'
with PdfPages(pdf_output) as pdf:
    fig,ax = plt.subplots()
    ax.scatter(umap_model_emb[:,0],umap_model_emb[:,1],s=3,c='k')
    ax.set_aspect('equal')
    ax.set_axis_off()
    ax.set_title('Reference Embedding')
    pdf.savefig()
    fig,ax = plt.subplots()
    ax.scatter(umap_model_emb[:,0],umap_model_emb[:,1],s=3,c='lightgrey')
    sns.kdeplot(umap_model_emb[:,0],umap_model_emb[:,1],cmap='binary_r',shade=False,gridsize=70,n_levels=14)
    ax.set_aspect('equal')
    ax.set_axis_off()
    ax.set_title('Reference Projected onto Reference Embedding')
    pdf.savefig()
    for i,proj in enumerate(projs):
        fig,ax = plt.subplots()
        ax.scatter(umap_model_emb[:,0],umap_model_emb[:,1],s=3,c='lightgrey')
        sns.kdeplot(proj[:,0],proj[:,1],cmap='binary_r',shade=False,gridsize=70,n_levels=14)
        ax.set_aspect('equal')
        ax.set_axis_off()
        ax.set_title('Query %(i)d Projected onto Reference Embedding' % vars())
        pdf.savefig()


