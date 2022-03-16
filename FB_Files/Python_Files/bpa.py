import pandas as pd
import numpy as np

results = pd.read_csv('WCA Database/WCA_export_Results.tsv', delimiter='\t')
raverage = pd.read_csv('WCA Database/WCA_export_RanksAverage.tsv', delimiter='\t')

raverage["eventId"] = raverage["eventId"].apply(lambda x: str(x))

events = list(raverage.eventId.unique())
exc_events = ["333ft", "magic", "mmagic", "666", "777", "333bf", "444bf", "555bf", "333fm"]
ao5_events = []
for event in events:
    if event not in exc_events:
        ao5_events.append(event)
        
def getMaxTime(event: str, place: int=20):
    x = raverage[raverage.eventId == event].reset_index(drop="index")
    for i, b in enumerate(x.best):
        if i == place - 1:
            return b

tenthplace = {event:getMaxTime(event) for event in ao5_events}

def getAVGs(event: str, tp: int):
    x1 = results[results.eventId == event]
    x2 = x1[x1.best <= tp]
    x3 = x2[x2.best > 0].reset_index(drop="index")
    return x3

def calcBPA(times: list):
    sortedtimes = np.sort(times)
    if sortedtimes[0] <= 0:
        if sortedtimes[1] <= 0:
            return -1
        return np.mean(sortedtimes[1:])
    else:
        return np.mean(sortedtimes[:3])

def main():
    for event in ao5_events:
        names = []
        countries = []
        comps = []
        bpas = []
        avgs = []
        tp = tenthplace[event]
        res = getAVGs(event, tp)
        print(f"There are {len(res)} averages to check for {event}.")
        for i, c in enumerate(res.personCountryId):
            bpa = calcBPA([res[f"value{j}"][i] for j in range(1, 5)])
            if 0 < bpa <= tp:
                names.append(res.personName[i])
                countries.append(c)
                comps.append(res.competitionId[i])
                bpas.append(round(bpa / 100, 2))
                a = res.average[i]
                if a <= 0:
                    avgs.append(a)
                else:
                    avgs.append(round(a / 100, 2))
        # Making the dataframe
        df = pd.DataFrame({"name":names, "country":countries, "comp":comps, "bpa":bpas, "average":avgs})
        df = df.sort_values("bpa").reset_index(drop="index").head(20)
        df.to_csv(f"bpa_{event}.csv", index=False)


if __name__ == "__main__":
    # Best Potential Averages
    main()
