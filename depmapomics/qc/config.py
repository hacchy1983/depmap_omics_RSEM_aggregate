from gsheets.api import Sheets
from taigapy import TaigaClient

# there are some issues in the older versions of omics data on virtual that this flag deals with
# some columns got renamed in the mutation file and some data was uploaded as tsv instead of csv
LEGACY_PATCH_FLAGS = {"rename_column": True, "tsv2csv": False}

# release ids on taiga
tc = TaigaClient()


def taiga_latest_version(dataset_name):
    return int(tc.get_dataset_metadata(dataset_name)["versions"][-1]["name"])


def taiga_latest_path(dataset_name):
    return {
        "name": dataset_name,
        "version": taiga_latest_version(dataset_name),
    }


# from depmapomics.qc.create_dataset import update_tentative_virtual
# update_tentative_virtual()
TENTATIVE_VIRTUAL = taiga_latest_path("tentative-virtual-d84e")

VIRTUAL_RELEASES = {
    "21Q4v2": {
        "internal": taiga_latest_path("internal-21q4v2-403b"),
        "ibm": taiga_latest_path("ibm-21q4v2-2d92"),
        "public": taiga_latest_path("public-21q4v2-103d"),
        "dmc": taiga_latest_path("dmc-21q4v2-0e7c"),
    },
    "21Q3": {
        "internal": {"name": "internal-21q3-fe4c", "version": 12},
        "ibm": {"name": "ibm-21q3-179f", "version": 8},
        "dmc": {"name": "dmc-21q3-482c", "version": 7},
        "public": {"name": "public-21q3-bf1e", "version": 7},
    },
    "21Q4": {
        "internal": taiga_latest_path("internal-21q4-ac0a"),
        "ibm": taiga_latest_path("ibm-21q4-4e18"),
        "dmc": taiga_latest_path("dmc-21q4-5725"),
        "public": taiga_latest_path("public-21q4-a0d6"),
    },
    "22Q1": {
        "internal": taiga_latest_path("internal-22q1-1778"),
        "ibm": taiga_latest_path("ibm-22q1-cce1"),
        "dmc": taiga_latest_path("dmc-22q1-d00a"),
        "public": taiga_latest_path("public-22q1-305b"),
    },
    "22Q2": {
        "internal": taiga_latest_path("internal-22q2-097a"),
        "ibm": taiga_latest_path("ibm-22q2-a71e"),
        "dmc": taiga_latest_path("dmc-22q2-5e51"),
        "public": taiga_latest_path("public-22q2-de04"),
    },
}  # release ids on taiga

PORTALS = ["ibm", "dmc", "public", "internal"]  # used for 'bookkeeping' markers
PORTAL = "dmc"  # used for 'not bookkeeping' markers
PREV_QUARTER = "22Q1"
NEW_QUARTER = "22Q2"

PREV_RELEASE = VIRTUAL_RELEASES[PREV_QUARTER][PORTAL]
NEW_RELEASE = VIRTUAL_RELEASES[NEW_QUARTER][PORTAL]
# NEW_RELEASE = TENTATIVE_VIRTUAL
PORTALS = [PORTAL]


LINES_TO_DROP_COMMON = {"ACH-001108", "ACH-001011", "ACH-001092"}
LINES_TO_DROP_DNA = LINES_TO_DROP_COMMON
LINES_TO_DROP_RNA = LINES_TO_DROP_COMMON | {"ACH-002778", "ACH-002745"}
LINES_TO_DROP = {"DNA": LINES_TO_DROP_DNA, "RNA": LINES_TO_DROP_RNA}


# original
# LINES_TO_RELEASE_SHEET = "https://docs.google.com/spreadsheets/d/1YuKEgZ1pFKRYzydvncQt9Y_BKToPlHP-oDB-0CAv3gE/edit?usp=sharing"

# copy of original with 21Q4v2 and 22Q1 combined into 22Q1
LINES_TO_RELEASE_SHEET = "https://docs.google.com/spreadsheets/d/1IO9GqeU8m3S_PJb4U2VCKbePVrxBA-k-7jp4A3bhxd8/edit?usp=sharing"

sheets_obj = Sheets.from_files("~/.client_secret.json", "~/.storage.json")
sheets = sheets_obj.get(LINES_TO_RELEASE_SHEET)
# LINES_TO_RELEASE = sheets.sheets[0]
LINES_TO_RELEASE_DF = sheets.find(NEW_QUARTER)
LINES_TO_RELEASE_DF = LINES_TO_RELEASE_DF.to_frame(header=0, index_col=None)
LINES_TO_RELEASE_DF.columns = LINES_TO_RELEASE_DF.columns.str.lower()


LINES_TO_RELEASE = {}
LINES_TO_RELEASE["public"] = set(LINES_TO_RELEASE_DF["public"].dropna())
LINES_TO_RELEASE["dmc"] = LINES_TO_RELEASE["public"] | set(
    LINES_TO_RELEASE_DF["dmc"].dropna()
)
LINES_TO_RELEASE["ibm"] = LINES_TO_RELEASE["dmc"] | set(
    LINES_TO_RELEASE_DF["ibm"].dropna()
)
LINES_TO_RELEASE["internal"] = LINES_TO_RELEASE["ibm"] | set(
    LINES_TO_RELEASE_DF["internal"].dropna()
)
IGNORE_FAILED_TO_RELEASE = False

# these are the columns that if merged with an older release (assuming that old data was not altered),
# should uniquely identify each row of the file to find equal values in each column
FUSIONS_MERGE_COLS = [
    "DepMap_ID",
    "LeftGene",
    "RightGene",
    "LeftBreakpoint",
    "RightBreakpoint",
    "SpliceType",
]
SEGMENT_CN_MERGE_COLS = ["DepMap_ID", "Chromosome", "Start", "End"]
MUTATIONS_MERGE_COLS = [
    "DepMap_ID",
    "Chromosome",
    "Start_position",
    "End_position",
    "Alternate_Allele",
]

# if there are new files that were added in the previous release, add them here
FILES_RELEASED_BEFORE = [
    "CCLE_expression",
    "CCLE_expression_proteincoding_genes_expected_count",
    "CCLE_RNAseq_transcripts",
    "CCLE_expression_transcripts_expected_count",
    "CCLE_expression_full",
    "CCLE_RNAseq_reads",
    "CCLE_fusions",
    "CCLE_fusions_unfiltered",
    "CCLE_gene_cn",
    "CCLE_segment_cn",
    "CCLE_mutations",
]

# correlation thresholds above which we consider two releases as 'similar'
CORRELATION_THRESHOLDS = {"CCLE_gene_cn": 0.99, "all_expressions": 0.98}

SKIP_ARXSPAN_COMPARISON = (
    True  # set to False if you want to test whether some arxspans were added/removed
)

PLOTS_OUTPUT_FILENAME_PREFIX = "/tmp/plots_"  # location/prefix for saving output plots

# all the file attributes
FILE_ATTRIBUTES = [
    {
        "file": "CCLE_expression",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "entrez",
        "omicssource": "RNA",
    },
    {
        "file": "CCLE_expression_proteincoding_genes_expected_count",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "entrez",
        "omicssource": "RNA",
    },
    {
        "file": "CCLE_RNAseq_transcripts",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "enst",
        "omicssource": "RNA",
    },
    {
        "file": "CCLE_expression_transcripts_expected_count",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "enst",
        "omicssource": "RNA",
    },
    {
        "file": "CCLE_expression_full",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "ensg",
        "omicssource": "RNA",
    },
    {
        "file": "CCLE_RNAseq_reads",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "ensg",
        "omicssource": "RNA",
    },
    {
        "file": "CCLE_fusions",
        "ismatrix": False,
        "omicssource": "RNA",
        "merge_cols": FUSIONS_MERGE_COLS,
        "expected_changed_cols": ["CCLE_count"],
    },
    {
        "file": "CCLE_fusions_unfiltered",
        "ismatrix": False,
        "omicssource": "RNA",
        "merge_cols": FUSIONS_MERGE_COLS,
        "expected_changed_cols": ["CCLE_count"],
    },
    # {'file': 'CCLE_ssGSEA', 'ismatrix': True, 'hasNA': False,'omicssource':'RNA', 'gene_id': None},
    {
        "file": "CCLE_gene_cn",
        "ismatrix": True,
        "hasNA": True,
        "gene_id": "entrez",
        "omicssource": "DNA",
    },
    {
        "file": "CCLE_segment_cn",
        "ismatrix": False,
        "omicssource": "DNA",
        "merge_cols": SEGMENT_CN_MERGE_COLS,
        "expected_changed_cols": [],
    },
    {
        "file": "CCLE_mutations",
        "ismatrix": False,
        "omicssource": "DNA",
        "merge_cols": MUTATIONS_MERGE_COLS,
        "expected_changed_cols": [],
    },
    {
        "file": "CCLE_mutations_bool_damaging",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "entrez",
        "omicssource": "DNA",
    },
    {
        "file": "CCLE_mutations_bool_hotspot",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "entrez",
        "omicssource": "DNA",
    },
    {
        "file": "CCLE_mutations_bool_otherconserving",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "entrez",
        "omicssource": "DNA",
    },
    {
        "file": "CCLE_mutations_bool_nonconserving",
        "ismatrix": True,
        "hasNA": False,
        "gene_id": "entrez",
        "omicssource": "DNA",
    },
]

# comment/uncomment to use all/subset of files for testing
# FILE_ATTRIBUTES = [
# x for x in FILE_ATTRIBUTES if (x["file"] in ["CCLE_segment_cn", "CCLE_gene_cn"])
# ]
# FILE_ATTRIBUTES = [x for x in FILE_ATTRIBUTES if (x['file'] in ['CCLE_mutations'])]
# FILE_ATTRIBUTES = [
# x for x in FILE_ATTRIBUTES if (x["file"].startswith("CCLE_mutations"))
# ]
# FILE_ATTRIBUTES = [
#     x for x in FILE_ATTRIBUTES if (x["omicssource"] in ["RNA"]) and x["ismatrix"]
# ]
# FILE_ATTRIBUTES = [
#     x
#     for x in FILE_ATTRIBUTES
#     if (x["file"] in ["CCLE_fusions", "CCLE_fusions_unfiltered"])
# ]

# the following information is used to create a tentative virtual
MUTATIONS_TAIGA_ID = "mutations-latest-ed72"
FUSIONS_TAIGA_ID = "fusions-95c9"
EXPRESSION_TAIGA_ID = "expression-d035"
CN_TAIGA_ID = "cn-achilles-version-06ca"
# CN_TAIGA_ID = 'cn-latest-d8d4'

TAIGA_IDS_LATEST = {
    MUTATIONS_TAIGA_ID: [
        ("CCLE_mutations", "merged_somatic_mutations_withlegacy"),
        (
            "CCLE_mutations_bool_damaging",
            "merged_somatic_mutations_boolmatrix_fordepmap_damaging",
        ),
        (
            "CCLE_mutations_bool_nonconserving",
            "merged_somatic_mutations_boolmatrix_fordepmap_othernoncons",
        ),
        (
            "CCLE_mutations_bool_otherconserving",
            "merged_somatic_mutations_boolmatrix_fordepmap_othercons",
        ),
        (
            "CCLE_mutations_bool_hotspot",
            "merged_somatic_mutations_boolmatrix_fordepmap_hotspot",
        ),
    ],
    FUSIONS_TAIGA_ID: [
        ("CCLE_fusions_unfiltered", "fusions_latest"),
        ("CCLE_fusions", "filteredfusions_latest"),
    ],
    EXPRESSION_TAIGA_ID: [
        ("CCLE_expression_full", "genes_tpm_logp1"),
        ("CCLE_RNAseq_transcripts", "transcripts_tpm_logp1"),
        ("CCLE_RNAseq_reads", "genes_expected_count"),
        ("CCLE_expression", "proteincoding_genes_tpm_logp1"),
        (
            "CCLE_expression_proteincoding_genes_expected_count",
            "proteincoding_genes_expected_count",
        ),
        ("CCLE_expression_transcripts_expected_count", "transcripts_expected_count"),
        # ('CCLE_ssGSEA', 'gene_sets_all')
    ],
    CN_TAIGA_ID: [
        ("CCLE_gene_cn", "achilles_gene_cn"),
        ("CCLE_segment_cn", "achilles_segment")
        # ('CCLE_gene_cn', 'merged_genecn_all'),
        # ('CCLE_segment_cn', 'merged_segments_all')
    ],
}
