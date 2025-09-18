import pandas as pd

def takeID(csr):
    av_records = 'client_data/av_rec.csv'
    df = pd.read_csv(av_records)
    csr_id = df[df.csr==csr].csr_id.to_list()[0]

    return csr_id.encode()
