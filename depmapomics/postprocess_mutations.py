import dalmatian as dm
import pandas as pd
from genepy.google.gcp import cpFiles
import numpy as np
from src.CCLE_postp_function import addAnnotation
from genepy.mutations import filterAllelicFraction, filterCoverage


def add_variant_annotation_column(maf):
    mutation_groups={
        "other conserving": ["5'Flank", "Intron", "IGR", "3'UTR", "5'UTR"],
        "other non-conserving":["In_Frame_Del", "In_Frame_Ins", "Stop_Codon_Del",
            "Stop_Codon_Ins", "Missense_Mutation", "Nonstop_Mutation"],
        'silent': ['Silent'],
        "damaging":['De_novo_Start_OutOfFrame','Frame_Shift_Del','Frame_Shift_Ins',
            'Splice_Site', 'Start_Codon_Del', 'Start_Codon_Ins', 'Start_Codon_SNP','Nonsense_Mutation']
    }

    rename = {}
    for k,v in mutation_groups.items():
        for e in v:
            rename[e] = k
    maf['Variant_annotation'] = [rename[i] for i in maf['Variant_Classification'].tolist()]
    return maf

def postprocess_mutations_filtered_wes(refworkspace, sample_set_name = 'all',
                                       output_file='/tmp/wes_somatic_mutations.csv'):
    refwm = dm.WorkspaceManager(refworkspace).disable_hound()
    filtered = refwm.get_sample_sets().loc[sample_set_name]['filtered_CGA_MAF_aggregated']
    print('copying aggregated filtered mutation file')
    cpFiles([filtered], "/tmp/mutation_filtered_terra_merged.txt")
    print('reading the mutation file')
    mutations = pd.read_csv('/tmp/mutation_filtered_terra_merged.txt', sep='\t', low_memory=False)
    mutations = mutations.rename(columns={"i_ExAC_AF":"ExAC_AF",
                                          "Tumor_Sample_Barcode":'DepMap_ID',
                                          "Tumor_Seq_Allele2":"Tumor_Allele"}).\
    drop(columns=['Center','Tumor_Seq_Allele1'])
    # mutations = annotate_likely_immortalized(mutations, TCGAlocs = ['TCGAhsCnt', 'COSMIChsCnt'], max_recurrence=0.05, min_tcga_true_cancer=5)
    print('writing CGA_WES_AC column')
    mutations['CGA_WES_AC'] = [str(i[0]) + ':' + str(i[1]) for i in np.nan_to_num(mutations[['t_alt_count','t_ref_count']].values,0).astype(int)]
    # apply version:
    # mutations['CGA_WES_AC'] = mutations[['t_alt_count', 't_ref_count']].fillna(0).astype(int).apply(lambda x: '{:d}:{:d}'.format(*x), raw=True, axis=1)
    print('filtering coverage')
    mutations = filterCoverage(mutations, loc=['CGA_WES_AC'], sep=':', cov=2)
    print('filtering allelic fractions')
    mutations = filterAllelicFraction(mutations, loc=['CGA_WES_AC'], sep=':', frac=0.1)
    print('adding NCBI_Build and strand annotations')
    mutations = addAnnotation(mutations, NCBI_Build='37', Strand="+")
    print('adding the Variant_annotation column')
    mutations = add_variant_annotation_column(mutations)
    print('saving results to output file')
    mutations.to_csv('/tmp/wes_somatic_mutations.csv', index=False)
    return mutations
