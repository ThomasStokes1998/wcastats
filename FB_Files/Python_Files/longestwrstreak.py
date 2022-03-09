import pandas as pd
from datetime import date

low_memory = False
results = pd.read_csv('WCA Database/WCA_export_Results.tsv', delimiter='\t')
competitions = pd.read_csv('WCA Database/WCA_export_Competitions.tsv', delimiter='\t')
persons = pd.read_csv('WCA Database/WCA_export_Persons.tsv', delimiter='\t')

# Longest WR streak but it doesn't reset when broken by another person

wrsingles = results[results.regionalSingleRecord == "WR"].reset_index(drop="index")
wraverages = results[results.regionalAverageRecord == "WR"].reset_index(drop="index")


def comp_date(complist: list):
    dates = []
    for c in complist:
        cinfo = competitions[competitions.id == c].reset_index(drop="index")
        y = cinfo.year[0]
        m = cinfo.month[0]
        d = cinfo.day[0]
        dates.append(date(y, m, d))
    return dates

wrsingles["date"] = comp_date(wrsingles.competitionId)
wraverages["date"] = comp_date(wraverages.competitionId)

wrsingles = wrsingles.sort_values("date").reset_index(drop="index")
wraverages = wraverages.sort_values("date").reset_index(drop="index")

events = list(results.eventId.unique())
retired_events = ["333mbo", "magic", "mmagic", "333ft"]
names = []
countries = []
streaks = []
types = []
startdates = []
enddates = []
for event in events:
    if event not in retired_events:
        # Single WR History
        evsingle = wrsingles[wrsingles.eventId == event].reset_index(drop="index")
        l = len(evsingle)
        for i in range(l):
            wcaid = evsingle.personId[i]
            if i == 0 or event == "333" and i == 1:
                currholder = wcaid
                startdate = evsingle.date[i]
            elif wcaid != currholder:
                enddate = evsingle.date[i]
                streak = (enddate - startdate).days
                if streak >= 365:
                    names.append(evsingle.personName[i-1])
                    countries.append(evsingle.personCountryId[i-1])
                    types.append(event + " single")
                    streaks.append(streak)
                    startdates.append(startdate)
                    enddates.append(enddate)
                currholder = wcaid
                startdate = enddate
            if i == l - 1:
                enddate = date.today()
                streak = (enddate - startdate).days
                if streak >= 365:
                    names.append(evsingle.personName[i])
                    countries.append(evsingle.personCountryId[i])
                    types.append(event + " single")
                    streaks.append(streak)
                    startdates.append(startdate)
                    enddates.append(enddate)
                
        # Average WR History
        evaverage = wraverages[wraverages.eventId == event].reset_index(drop="index")
        l = len(evaverage)
        if l > 0:
            for i in range(l):
                wcaid = evaverage.personId[i]
                if i == 0:
                    currholder = wcaid
                    startdate = evaverage.date[i]
                elif wcaid != currholder:
                    enddate = evaverage.date[i]
                    streak = (enddate - startdate).days
                    if streak >= 365:
                        names.append(evaverage.personName[i-1])
                        countries.append(evaverage.personCountryId[i-1])
                        types.append(event + " average")
                        streaks.append(streak)
                        startdates.append(startdate)
                        enddates.append(enddate)
                    currholder = wcaid
                    startdate = enddate
                if i == l - 1:
                    enddate = date.today()
                    streak = (enddate - startdate).days
                    if streak >= 365:
                        names.append(evaverage.personName[i])
                        countries.append(evaverage.personCountryId[i])
                        types.append(event + " average")
                        streaks.append(streak)
                        startdates.append(startdate)
                        enddates.append(enddate)

# Making the CSV File
df = pd.DataFrame({"Name": names, "Country": countries, "Streak": streaks, "Type": types,
                   "Start Date": startdates, "End Date": enddates})

df = df.sort_values("Streak", ascending=False).reset_index(drop="index")
if __name__ == "__main__":
    df.to_csv("longestwrstreak.csv", index=False)
