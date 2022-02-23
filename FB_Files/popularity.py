import pandas as pd
import statistics
from datetime import date

low_memory = False
persons = pd.read_csv("WCA Database/WCA_export_Persons.tsv", delimiter='\t')
results = pd.read_csv('WCA Database/WCA_export_Results.tsv', delimiter='\t')
competitions = pd.read_csv('WCA Database/WCA_export_Competitions.tsv', delimiter='\t')
countries = pd.read_csv('WCA Database/WCA_export_Countries.tsv', delimiter='\t')
# Country Kinch Ranks History

# Ordering the competition dataframe
def orderComps():
    dates = []
    for i, _ in enumerate(competitions.id):
        y = competitions.year[i]
        m = competitions.month[i]
        d = competitions.day[i]
        dates.append(date(y, m, d))
    competitions["date"] = dates
orderComps()

# Main DataFrame
recordrounds = results.dropna(thresh=1, subset=["regionalSingleRecord", "regionalAverageRecord"])
recordrounds["date"] = recordrounds["competitionId"].apply(lambda x: competitions[competitions.id == x].reset_index().date[0])
recordrounds = recordrounds.sort_values("date").reset_index(drop="index")
recordrounds = recordrounds[["date", "eventId", "best", "average", "personCountryId"]]
events = list(recordrounds.eventId.unique())

# Dictionaries
t1 = 360_000
edex = {event:i for i, event in enumerate(events)}
print(edex)
countrylist = list(recordrounds.personCountryId.unique())
singlenrs = {country:[t1, t1, t1, t1, t1, t1, t1, t1, t1, t1, 80, t1, t1, t1, t1, t1, 0, 0, t1, t1, t1] 
for country in countrylist}
averagenrs = {country:[t1, t1, t1, t1, t1, t1, t1, t1, t1, t1, 8000, t1, t1, t1, t1, t1, 0, 0, t1, t1, t1] 
for country in countrylist}
wrs = {"single":[t1, t1, t1, t1, t1, t1, t1, t1, t1, t1, 80, t1, t1, t1, t1, t1, 0, 0, t1, t1, t1], 
"average":[t1, t1, t1, t1, t1, t1, t1, t1, t1, t1, 8000, t1, t1, t1, t1, t1, 0, 0, t1, t1, t1]}
dfdict = {"country":[country for country in countrylist], 
"continent":[countries[countries.id == country].reset_index().continentId[0] for country in countrylist]}


def main():
    currdate = recordrounds.date[0]
    regevents = []
    retired_events = []
    for i, newdate in enumerate(recordrounds.date):
        # Check if it is a new month
        if newdate.month != currdate.month:
            # Update Kinch Ranks
            if currdate.year > 1982:
                print(f"Updating kinch ranks for {currdate.day}/{currdate.month}/{currdate.year}")
                kranks = []
                for country in countrylist:
                    snrs = singlenrs[country]
                    anrs = averagenrs[country]
                    kr = []
                    for event in regevents:
                        if event not in retired_events:
                            e = edex[event]
                            wrsing = wrs["single"][e]
                            wravg = wrs["average"][e]
                            if event in ["333mbf", "333mbo"]:
                                krs = 100 * snrs[e] / wrsing
                                kr.append(krs)
                            else:
                                krs = 100 * wrsing / snrs[e]
                                kra = 100 * wravg / anrs[e]
                                # For before there was an official single/average in the events
                                if wravg == 360_000:
                                    kr.append(krs)
                                elif wrsing == 360_000:
                                    kr.append(kra)
                                else:
                                    kr.append(max(krs, kra))
                    kranks.append(round(statistics.mean(kr), 2))
                dfdict[f"{currdate.month}/{currdate.year}"] = kranks
                pd.DataFrame(dfdict).to_csv("countrykrankshist.csv", index=False)
                # Update official events
                if newdate.year == 2009 and currdate.year != 2009:
                    retired_events.append("333mbo")
                elif newdate.year == 2014 and currdate.year != 2014:
                    retired_events.append("magic")
                    retired_events.append("mmagic")
                elif newdate.year == 2020 and currdate.year != 2020:
                    retired_events.append("333ft")
            currdate = newdate
        # Get results
        event = recordrounds.eventId[i]
        if event not in regevents:
            regevents.append(event)
        e = edex[event]
        country_ = recordrounds.personCountryId[i]
        single = recordrounds.best[i]
        avg = recordrounds.average[i]
        # Update Dictionaries
        if event in ["333mbf", "333mbo"]:
            if event == "333mbf":
                single = 99 - (single // 1e7)
            else:
                data = single // 1e5
                a = data % 100
                s = 199 - (data // 100)
                single = 2 * s - a
            if single > singlenrs[country_][e]:
                singlenrs[country_][e] = single
                if single > wrs["single"][e]:
                    wrs["single"][e] = single
        else:
            if 0 < single < singlenrs[country_][e]:
                singlenrs[country_][e] = single
                if single < wrs["single"][e]:
                    wrs["single"][e] = single
            if 0 < avg < averagenrs[country_][e]:
                averagenrs[country_][e] = avg
                if avg < wrs["average"][e]:
                    wrs["average"][e] = avg
                    
if __name__ == "__main__":
    main()
