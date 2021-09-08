import pandas as pd

data = [
    {"BUSSTOPID": 'BS1472'},
    {"BUSSTOPID": 'BS1473'},
]

df = pd.DataFrame(data)

print(df.head())
print(df.info())

df = df.append(pd.Series(), ignore_index=True)
df = df.append(pd.Series(data={"BUSSTOPID": 'BS0001'}, name="test"))
print(df)
