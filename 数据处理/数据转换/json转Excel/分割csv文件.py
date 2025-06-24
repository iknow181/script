import pandas as pd
chunk_size = 100000
for i, chunk in enumerate(pd.read_csv("output/converted.csv", chunksize=chunk_size)):
    chunk.to_csv(f"chunk/chunk_{i}.csv", index=False)