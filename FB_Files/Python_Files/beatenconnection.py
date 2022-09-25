import pandas as pd
import time
import random

low_memory = False
results = pd.read_csv('WCA Database/WCA_export_Results.tsv', delimiter='\t')
# competitions = pd.read_csv('WCA Database/WCA_export_Competitions.tsv', delimiter='\t')
persons = pd.read_csv('WCA Database/WCA_export_Persons.tsv', delimiter='\t')

bld_events = ["333bf", "444bf", "555bf", "333mbf", "333mbo"]

# Fasted known alg; run time ~ 0.04 - 0.1s
def getAllComps(wcaid: str, df) -> list:
    return list(df[df.personId == wcaid].competitionId.unique())

def getAllChildren(wcaid: str, beaten: bool, er, excids: list = None) -> tuple:
    # Beaten: True - all competitors that have beaten by wcaid
    if excids is None:
        excids = [wcaid]
    children = []
    comps = getAllComps(wcaid, er)
    for c in comps:
        x1 = er[er.competitionId == c].reset_index(drop="index")
        for r in list(x1.roundTypeId.unique()):
            x2 = x1[x1.roundTypeId == r].sort_values("pos").reset_index(drop="index")
            pastid = False
            for i, w in enumerate(x2.personId):
                if w == wcaid:
                    if beaten:
                        break
                    pastid = True
                if w not in excids:
                    # Check for DNF results
                    if x2.eventId[i] not in bld_events and x2.average[i] <= 0 or x2.eventId[i] in bld_events and x2.best[i] <= 0:
                        break
                    if beaten or not beaten and pastid:
                        children.append(w)
                        excids.append(w)
    return children, excids

def personConnection(person1id: str, person2id: str, event: str="333", showprint: bool=False) -> list:
    er = results[results.eventId == event].reset_index(drop="index")
    searching = True
    p1excids = [person1id]
    p1graph = {0:[person1id]}
    p1parents = {}
    p2excids = [person2id]
    p2graph = {0:[person2id]}
    p2parents = {}
    d1, d2 = 1, 1
    while searching:
        l1, l2 = len(p1graph[d1-1]), len(p2graph[d2-1])
        # Expands the smallest branch first
        if l1 <= l2:
            # Looking for people person1 has beaten
            l = len(p1graph[d1-1])
            p1graph[d1] = []
            t0 = time.time()
            for i, wcaid in enumerate(p1graph[d1-1]):
                if i % 10 == 0 and i > 0 and showprint:
                    t = time.time()-t0
                    print(f"Done {i}/{l} {round(100 * i / l, 2)}% complete. Time elapsed: {round(t)}s")
                    print(f"Estimated time remaining: {round(t * (l/i - 1))}s")
                children, p1excids = getAllChildren(wcaid, True, er, p1excids)
                for child in children:
                    p1parents[child] = wcaid
                    if child in p2graph[d2-1]:
                        # Found a connection (must be minimal by the construction of the algorithm).
                        if child == person2id:
                            return [person1id, person2id]
                        half1 = []
                        while child != person1id:
                            half1.append(child)
                            child = p1parents[child]
                        returnlist = [person1id]
                        for c in reversed(half1):
                            returnlist.append(c)
                        if len(half1) == 0:
                            return [person1id, person2id]
                        child = half1[0]
                        child = p2parents[child]
                        while child != person2id:
                            returnlist.append(child)
                            child = p2parents[child]
                        returnlist.append(person2id)
                        return returnlist
                p1graph[d1] += children
            print(f"Time elapsed for {person1id} at degree {d1} = {round(time.time() - t0)}s. Size={len(p1graph[d1])}")
            if len(p1graph[d1]) == 0:
                if showprint:
                    print(f"There is no link between {person1id} and {person2id}.")
                return [person1id]
            d1 += 1

        # looking for people person2 has been beaten by
        l1, l2 = len(p1graph[d1-1]), len(p2graph[d2-1])
        if l2 <= l1:
            l = len(p2graph[d2-1])
            p2graph[d2] = []
            t0 = time.time()
            for i, wcaid in enumerate(p2graph[d2-1]):
                if i % 10 == 0 and i > 0 and showprint:
                    t = time.time()-t0
                    print(f"Done {i}/{l} {round(100 * i / l, 2)}% complete. Time elapsed: {round(t)}s")
                    print(f"Estimated time remaining: {round(t * (l/i - 1))}s")
                children, p2excids = getAllChildren(wcaid, False, er, p2excids)
                for child in children:
                    p2parents[child] = wcaid
                    if child in p1graph[d1-1]:
                        # Found a connection (must be minimal by the construction of the algorithm).
                        if child == person1id:
                            return [person1id, person2id]
                        half1 = []
                        while child != person1id:
                            half1.append(child)
                            child = p1parents[child]
                        returnlist = [person1id]
                        for c in reversed(half1):
                            returnlist.append(c)
                        if len(half1) == 0:
                            return [person1id, person2id]
                        child = half1[0]
                        child = p2parents[child]
                        while child != person2id:
                            returnlist.append(child)
                            child = p2parents[child]
                        returnlist.append(person2id)
                        return returnlist
                p2graph[d2] += children
            print(f"Time elapsed for {person2id} at degree {d2} = {round(time.time() - t0)}s. Size={len(p2graph[d2])}")
            if len(p2graph[d2]) == 0:
                if showprint:
                    print(f"There is no link between {person1id} and {person2id}.")
                return [person1id]
            d2 += 1
    return

# Finds all competitor degree d from a competitor and prints when it finds a specific competitor.
def eventPath(person1id: str, person2id: str="2017STOK03", event: str = "333", showprint: bool=False):
    er = results[results.eventId == event].reset_index(drop="index")
    excids = [person1id]
    # Key = degree, entries = wcaids
    maingraph = {0:[person1id]}
    d = 1
    l = len(maingraph[d-1])
    while l > 0:
        l = len(maingraph[d-1])
        maingraph[d] = []
        t0 = time.time()
        for i, wcaid in enumerate(maingraph[d-1]):
            if showprint and i % 10 == 0 and i > 0:
                t = time.time()-t0
                print(f"Done {i}/{l} {round(100 * i / l, 2)}% complete. Time elapsed: {round(t)}s")
                print(f"Estimated time remaining: {round(t * (l/i - 1))}s")
            children, excids = getAllChildren(wcaid, True, er, excids)
            if person2id in children:
                print(f"{person2id} is degree {d} from {person1id}. Path = {person1id} {wcaid} {person2id}.")
            maingraph[d] += children
        print(f"Time elapsed for degree {d} = {round(time.time() - t0)}s")
        print(f"There are {len(maingraph[d])} competitors degree {d} from {person1id}. Growth = {round(len(maingraph[d])/l,2)}")
        d += 1
    return

def findLongPath(attempts: int , event: str="333"):
    evids = list(results[results.eventId == event].personId.unique())
    pathlengths = []
    pldict = {i:0 for i in range(11)}
    maxpath = []
    pl = len(evids)
    tf = time.time()
    for a in range(attempts):
        # Find two random ids
        a1 = random.randrange(0, pl)
        a2 = random.randrange(0, pl)
        p1 = evids[a1]
        c1 = persons[persons.id == p1].reset_index(drop="index").countryId[0]
        p2 = evids[a2]
        c2 = persons[persons.id == p2].reset_index(drop="index").countryId[0]
        print(f"Finding a connection between {p1} from {c1} and {p2} from {c2}. ({a+1}/{attempts})")
        ta = time.time()
        path_list = personConnection(p1, p2, event)
        print(f"Time to find path = {round(time.time()-ta)}s.")
        l = len(path_list)
        if l > 1:
            if len(pathlengths) == 0 or l-1 > max(pathlengths):
                maxpath = path_list
            pathlengths.append(l-1)
            if l - 1 not in pldict:
                pldict[l - 1] = 1
            else:
                pldict[l - 1] += 1
            print(f"Path length = {l-1}, {path_list}")
        else:
            pldict[0] += 1
            print(f"No connection between {p1} and {p2}.")
        if a % 10 == 9 and a < attempts - 1:
            print(f"Time Elapsed: {round(time.time()-tf)}s")
            print(f"Frequencies = {pldict}")
    print(f"Longest path = {max(pathlengths)}, {maxpath}")
    print(f"Frequencies = {pldict}")

if __name__ == "__main__":
    personConnection("2016MAHA07","2012PARK03")
