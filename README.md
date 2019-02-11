# umap_projection

This code enables the projection of single-cell RNA-seq profiles from one dataset into the UMAP embedding coordinates of a different dataset. While UMAP includes a "transform" function for this purpose, it does not allow the use of Spearman's correlation as a similarity metric. Spearman's correlation is particularly useful in this context because 1) the cluster_diffex pipeline uses Spearman's correlation as a similarity metric and 2) the non-parametric nature of Spearman's correlation allows projection of scRNA-seq data generated by completely different methods from that used in the original embedding.  For example, one could project SMART-seq data (e.g. TPM data) onto a UMAP embedding generated using 10x Genomics Chromium data (e.g. molecular counting data). This repository includes code for computing the transformation, generating figures, and also a modified version of umap_.py (the main UMAP executable) that can accommodate the use of Spearman's correlation coefficient as a similarity metric.

Requirements:

1) Python 3.6 or higher
2) Numpy
3) Scikit-learn
4) UMAP
5) Scipy
6) Numba


Suggested usage:

0) Install dependencies.

1) Clone this repository.

2) Copy the main executable for UMAP in your current installation to a temporary file (e.g. "cp path_to_UMAP/umap_.py path_to_UMAP/umap_tmp.py").

3) Replace the main executable for UMAP in your current installation with the file "umap_.py" in this repository (e.g. "cp umap_projection/umap_.py path_to_UMAP/umap_.py").

4) Run umap_transform.py.  Example usage:

python umap_transform.py PP001 markers.txt PP017onPP001 20 PP017.used_genes.txt PP017

where PP017 is the scRNA-seq dataset that you want to project onto PP001.  

For this example, the program assumes that there are a directories called "PP001" and "PP017" that contain files called "PP001.matrix.txt" and "PP017.matrix.txt", respectively.  Further, it assumes that these files contain count matrices for the two datasets with the format GID\tSYMBOL\tCTS_CELL1\tCTS_CELL2... The program also assumes that the first column of markers.txt contains the GIDs for the marker genes used to cluster PP001 (e.g. could be markers identified from the drop-out or CV curve). Here, the number "20" is the value of k for the knn graph generated by UMAP, "PP017onPP001" is the prefix for all of the output files, and "PP017.used_genes.txt" is a file containing the set of markers actually used for the UMAP embedding and projection.  Note that if PP017 is missing GIDs from "markers.txt", then "PP017.used_genes.txt" will contain fewer GIDs than "markers.txt".

