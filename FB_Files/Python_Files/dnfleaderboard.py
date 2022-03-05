import pandas as pd

results = pd.read_csv('WCA Database/WCA_export_Results.tsv', delimiter='\t')

def main():
    dnfdict = {}
    namedict = {}
    countrydict = {}
    for i in range(1, 6):
        res = results[results[f"value{i}"] == -1].reset_index(drop="index")
        print(f"For value {i} there are {len(res)} dnfs from {len(res.personId.unique())} ids to enter.")
        for j, wcaid in enumerate(res.personId):
            if wcaid not in dnfdict:
                dnfdict[wcaid] = 0
                namedict[wcaid] = res.personName[j]
                countrydict[wcaid] = res.personCountryId[j]
            dnfdict[wcaid] += 1
    print(f"Found {len(dnfdict)} competitors with at least one dnf.")
    df = pd.DataFrame({"name":[namedict[x] for x in namedict], 
    "country":[countrydict[x] for x in countrydict], 
    "DNFs":[dnfdict[x] for x in dnfdict]})
    df = df.sort_values("DNFs", ascending=False).reset_index(drop="index")
    print(df.head(10))
    df.to_csv("dnfleaderboard.csv", index=False)


if __name__ == "__main__":
    # Most DNF Singles
    main()
