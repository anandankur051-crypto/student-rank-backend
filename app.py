from fastapi import FastAPI, HTTPException
import pandas as pd
import os

app = FastAPI()

# -----------------------------
# Load main CSV (overall ranks)
# -----------------------------
df = pd.read_csv("final_rank_list.csv")
df["roll_no"] = df["roll_no"].astype(str)

# -----------------------------
# Branch CSV folder
# -----------------------------
BRANCH_FOLDER = "branch_wise_ranks"

# -----------------------------
# Branch code → branch filename
# -----------------------------
BRANCH_CODE_MAP = {
    "UBT": "Bio_Tech",
    "UCE": "Civil",
    "UCS": "Computer",
    "UCA": "CS_AI",
    "UCD": "CS_with_Data_Science",
    "UCM": "MAC",
    "UCB": "CS_with_Big_Data",
    "UCI": "CS_IOT",
    "UEE": "Electrical",
    "UEC": "Electronics_and_Communication",
    "UEI": "EIOT",
    "UEV": "ECE_VLSI",
    "UEA": "ECAM_AI_ML",
    "UIT": "Information_Technology",
    "UIN": "ITNS",
    "UIC": "ICE",
    "UME": "Mechanical",
    "UMV": "Mechanical_Electric_Vehicles"
}

def extract_branch_from_roll(roll_no: str):
    for code, branch in BRANCH_CODE_MAP.items():
        if code in roll_no:
            return branch
    return None

# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {"status": "API running"}

# -----------------------------
# Get student overall + branch rank
# -----------------------------
@app.get("/user/rank/{roll_no}")
def get_rank(roll_no: str):
    user = df[df["roll_no"] == roll_no]

    if user.empty:
        raise HTTPException(status_code=404, detail="Roll number not found")

    user_data = user.iloc[0].to_dict()

    branch_name = extract_branch_from_roll(roll_no)
    if not branch_name:
        raise HTTPException(
            status_code=500,
            detail="Unable to extract branch from roll number"
        )

    branch_file = os.path.join(
        BRANCH_FOLDER,
        f"{branch_name}_rank_list.csv"
    )

    if not os.path.exists(branch_file):
        raise HTTPException(
            status_code=500,
            detail="Branch rank file not found"
        )

    branch_df = pd.read_csv(branch_file)
    branch_df["roll_no"] = branch_df["roll_no"].astype(str)

    branch_user = branch_df[branch_df["roll_no"] == roll_no]
    if branch_user.empty:
        raise HTTPException(
            status_code=500,
            detail="Branch rank not found for student"
        )

    user_data["branch"] = branch_name
    user_data["branch_rank"] = int(branch_user.iloc[0]["branch_rank"])

    return user_data

# -----------------------------
# Get full branch-wise rank list
# -----------------------------
@app.get("/branch/{branch_name}")
def get_branch_rank(branch_name: str):
    file_path = os.path.join(
        BRANCH_FOLDER,
        f"{branch_name}_rank_list.csv"
    )

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Branch not found")

    branch_df = pd.read_csv(file_path)
    return branch_df.to_dict(orient="records")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

