import os
import sys
from secret_config import this


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"please provide at least 1 argument")
    test = this['acc_project']
    prd = this['prd_project']
    service = this['service']
    for i, arg in enumerate(sys.argv):
        if arg == '-acc':
            os.system(f"gcloud config set project {test}")
            os.system("gcloud config list")
            os.system(f"gcloud builds submit --tag gcr.io/{test}/{service}")
            continue
        if arg == "-prd":
            os.system(f"gcloud config set project {prd}")
            print("switched to production environment")
            os.system(f"gcloud builds submit --tag gcr.io/{prd}/{service}")
            os.system(f"gcloud config set project {test}")
            print("returned to test environment")
            continue
        if arg == "-h":
            print("please pick an environment ready for deploy.  -acc, -prd.  Can be stacked")
            continue

