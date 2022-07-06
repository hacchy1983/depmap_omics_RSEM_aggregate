from depmapomics import vcf
from genepy import mutations
import sys
import pyarrow.parquet as pq
import pyarrow as pa
from genepy.utils import helper as h
import os

vcf_filename = sys.argv[1]
sample_name = (
    sys.argv[2] if len(sys.argv) > 2 else vcf_filename.split("/")[-1].split(".")[0]
)
n_rows = int(sys.argv[3]) if len(sys.argv) > 3 else 500_000
use_multi = "true" == sys.argv[4] if len(sys.argv) > 4 else False
opencravat = "true" == sys.argv[5] if len(sys.argv) > 5 else False
force_keep = sys.argv[6].split(",") if len(sys.argv) > 6 else []
whitelist = "true" == sys.argv[7] if len(sys.argv) > 7 else False
annotators = sys.argv[8].split(",") if len(sys.argv) > 8 else []

prev_cols = []

print(
    "inputs: vcf_filename:",
    vcf_filename,
    ", sample_name:",
    sample_name,
    ", n_rows:",
    n_rows,
    ", use_multi:",
    use_multi,
    ", opencravat:",
    opencravat,
    ", force_keep:",
    force_keep,
)

tobreak = False

loc = os.path.dirname(os.path.abspath(__file__))

oncogene = h.fileToList(loc + "/oncokb_dm/data/onocogene_oncokb.txt")
tumor_suppressor_list = h.fileToList(
    loc + "/oncokb_dm/data/tumor_suppressor_oncokb.txt"
)

for i in range(10_000):
    # read in vcf as a df
    vcf_file, _, _ = mutations.vcf_to_df(
        vcf_filename,
        additional_cols=["PON"],
        parse_filter=True,
        force_keep=force_keep,
        drop_null=False,
        cols_to_drop=[
            "clinvar_vcf_mc",
            "oreganno_build",
            "gt",
            "ad",
            "af",
            "dp",
            "f1r2",
            "f2r1",
            "fad",
            "sb",
            "pid",
            "pl",
            "ps",
            "gq",
            "pgt",
            "gencode_34_chromosome",
        ],
        nrows=n_rows,
        skiprows=n_rows * i,
    )
    if "PID" not in vcf_file.columns.tolist():
        vcf_file["PID"] = ""
    filen = len(vcf_file)
    if filen < n_rows:
        # we have reached the end:
        tobreak = True

    # improve
    vcf_file = vcf.improve(
        vcf_file,
        force_list=["oc_genehancer__feature_name"],
        split_multiallelic=use_multi,
        annotators=annotators,
    )

    # checking we have the same set of columns
    cols = vcf_file.columns.tolist()
    if i == 0:
        prev_cols = cols
    elif set(cols) != set(prev_cols):
        raise ValueError(
            "we are removing different sets of columns",
            cols,
            list(set(cols) ^ set(prev_cols)),
        )
    elif len(cols) != len(prev_cols):
        raise ValueError("some columns have duplicate values", prev_cols, cols)
    elif cols != prev_cols:
        vcf_file = vcf_file[prev_cols]

    # save full
    # need pyarrows
    print("to parquet")
    pq.write_to_dataset(
        pa.Table.from_pandas(vcf_file), root_path=sample_name + "-maf-full.parquet"
    )

    # save maf
    print("saving maf")
    if i == 0:
        vcf.to_maf(
            vcf_file,
            sample_name,
            only_somatic=True,
            only_coding=True,
            whitelist=whitelist,
            drop_multi=True,
            oncogenic_list=oncogene,
            tumor_suppressor_list=tumor_suppressor_list,
            tokeep={**vcf.TOKEEP_BASE, **vcf.TOKEEP_ADD},
            index=False,
        )
    else:
        vcf.to_maf(
            vcf_file,
            sample_name,
            only_somatic=True,
            only_coding=True,
            whitelist=whitelist,
            drop_multi=True,
            mode="a",
            header=False,
            oncogenic_list=oncogene,
            tumor_suppressor_list=tumor_suppressor_list,
            tokeep={**vcf.TOKEEP_BASE, **vcf.TOKEEP_ADD},
            index=False,
        )
    del vcf_file
    if tobreak:
        break
print("finished, processed {} rows".format((n_rows * i) + filen))
