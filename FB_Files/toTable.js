async function toTable(url, name=nameFilter, country=countryFilter, id="table-container", maxRows=1001) {
    let data = await fetch(url);
    let rawData = await data.text();
    let rows = rawData.split("\r\n");
    let rowNum = rows.length;
    if (rowNum < maxRows) {
        maxRows = rowNum
    };
    // initialise different table components
    let table = document.createElement("table");
    table.id = "myTable";
    let theader = table.createTHead();
    let tbody = table.createTBody();
    tbody.id = "table-body";
    let rowCounter = 0;
    for (i = 0; i < rowNum; i++) {
      if (rowCounter > maxRows) {
        break;
      }
        let row  = rows[i];
        let elements = row.split(",");
        // header
        if (i === 0) {
            let tr = theader.insertRow();
            for (j = 0; j < elements.length; j++) {
                let th = document.createElement("th");
                th.innerHTML = elements[j];
                // Adds sort on clicking header
                th.addEventListener("click", ascSort(j));
                tr.appendChild(th);
            }
        // body
        } else {
            // Check if name and country in row
            let addRow = true;
            if (name != "" && !elements[0].includes(name)) {
              addRow = false;
            }
            else if (country != "" && !elements[1].includes(country)) {
              addRow = false;
            }
            if (addRow){
              let tr = tbody.insertRow();
              for (j = 0; j < elements.length; j++) {
                  let newCell = tr.insertCell();
                  newCell.appendChild(document.createTextNode(elements[j]));
              }
              rowCounter++;
            }
        };
    };
    document.getElementById(id).appendChild(table);
    // Ascending / Descending toggle
    asc = false;
    function ascSort(c) {
    return function() {
        // Toggles between ascending and descending
        if (asc === true) {
            asc = false;
        }else {
            asc = true
        }
        // Quick Sort Algorithm
        let colList = toList(c);
        let colList2 = toList(c);
        let qsList = quickSort(colList2, 0, colList.length - 1, asc);
        let iList = indexList(colList, qsList);
        swapTable(iList, id, ascSort);
        // bubbleSort(c, asc); reliable but slow, only re-activate if quick sort breaks
      }
    }
}

function configTable(event, id="table-container", maxRows=rowMax) {
  document.getElementById("myTable").remove();
  toTable(`CSV_Files/bpa_${event}.csv`, id, maxRows);
  currEvent = event;
}

function setName(url) {
  input = document.getElementById("nameInput");
  nameFilter = input.value
  document.getElementById("myTable").remove();
  toTable(url, name=nameFilter, country=countryFilter)
}

function setCountry(url) {
  input = document.getElementById("countryInput");
  countryFilter = input.value
  document.getElementById("myTable").remove();
  toTable(url, name=nameFilter, country=countryFilter)
}


let currEvent = '333';
let rowMax = 20;
let nameFilter = ""
let countryFilter = ""
// Credit to https://www.guru99.com/quicksort-in-javascript.html for the Quick Sort algorithm

// Convert a HTML column to a list
function toList (colNum) {
  let numString = "0123456789";
  let table = document.getElementById("myTable");
  let allRows = table.rows;
  let colList = [];
  let number = true;
  for (i=1; i<(allRows.length); i++) {
    let x = allRows[i].getElementsByTagName("TD")[colNum];
    // Checking for data type (html text formatted as string)
    if (i === 1 && numString.search(x.innerHTML[0]) == -1) {
      number = false;
    };
    if (number) {
      colList.push(Number(x.innerHTML));
    } else {
      colList.push(x.innerHTML);
    }
  }
  return colList;
};

// Swaps two elements in a list
function swap(colList, leftIndex, rightIndex){
  var temp = colList[leftIndex];
  colList[leftIndex] = colList[rightIndex];
  colList[rightIndex] = temp;
};

function floor(x) {
  let y = String(x);
  if (y.search(".") == -1) {
    return x
  } else {
    return Number(y.split(".")[0])
  }
};

function partition(colList, left, right, asc) {
  const pivot = colList[floor((left + right) / 2)];
  if (typeof colList[0] === "number") {
    number = true;
  } else {
    number = false;
  }
  let i = left;
  let j = right;
  while (i <= j) {
    // Sorting Numbers
    if (number) {
      if (asc) {
        while (colList[i] < pivot) {
          i++;
        }
        while (colList[j] > pivot) {
          j--;
        }
      } else {
        while (colList[i] > pivot) {
          i++;
        }
        while (colList[j] < pivot) {
          j--;
        }
      }
      
    // Sorting Strings
    } else {
      if (asc) {
        while (colList[i].toLowerCase() < pivot.toLowerCase()) {
          i++;
        }
        while (colList[j].toLowerCase() > pivot.toLowerCase()) {
          j--;
        }
      } else {
        while (colList[i].toLowerCase() > pivot.toLowerCase()) {
          i++;
        }
        while (colList[j].toLowerCase() < pivot.toLowerCase()) {
          j--;
        }
      }
      
    }
    if (i <= j) {
      swap(colList, i, j);
      i++;
      j--;
    }
  }
  return i;
};

function quickSort(colList, left, right, asc=true) {
  let index = 0;
  if (colList.length > 1) {
    index = partition(colList, left, right, asc);
    if (left < index - 1) {
      quickSort(colList, left, index - 1, asc);
    }
    if (index < right) {
      quickSort(colList, index, right, asc);
    }
  }
  return colList;
};


function indexList(colList, qsList) {
  let iList = [];
  for (i = 0; i < qsList.length; i++) {
    let q = qsList[i]
    for (j = 0; j < colList.length; j++) {
      let c = colList[j];
      if (q === c && iList.includes(j) === false) {
        iList.push(j);
        break
      }
    }
  }
  return iList
};

function swapTable(iList, id, ascSort) {
  // New idea: have the function clear out the tbody tag and re assemble it sorted
  let table = document.getElementById("myTable");
  let allRows = table.rows;
  let newTable = document.createElement("table");
  newTable.id = "myTable"
  let newThead = newTable.createTHead();
  let newTbody = newTable.createTBody();
  newTbody.id = "table-body"; 
  for (i = 0; i < allRows.length; i++) {
    if (i === 0) {
      let row = newThead.insertRow();
      let newRow = allRows[0]
      let headers = newRow.getElementsByTagName("TH");
      for (j = 0; j < headers.length; j++) {
        let th = document.createElement("th");
        th.innerHTML = headers[j].innerHTML;
        // Adds sort on clicking header
        th.addEventListener("click", ascSort(j));
        row.appendChild(th);
      }
    } else {
      let row = newTbody.insertRow()
      let newRow = allRows[iList[i-1]+1]
      let elements = newRow.getElementsByTagName("TD")
      for (j = 0; j < elements.length; j++) {
        let newCell = row.insertCell();
        newCell.appendChild(document.createTextNode(elements[j].innerHTML));
      }
    }
  }
  table.remove();
  document.getElementById(id).appendChild(newTable);
};

// Credit to w3schools.com for the Bubble Sort algorithm
// Archived in case quick sort algorithm breaks
function bubbleSort(colNum, asc=true) {
  let numString = "0123456789";
  let table = document.getElementById("myTable");
  let switching = true;
  /* Make a loop that will continue until
  no switching has been done: */
  console.log("Sorting in Progress");
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    let allRows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (allRows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      let x = allRows[i].getElementsByTagName("TD")[colNum];
      let y = allRows[i + 1].getElementsByTagName("TD")[colNum];
      // Check if the two rows should switch place:
      if (numString.search(x.innerHTML[0]) != -1) {
          if (Number(x.innerHTML) > Number(y.innerHTML) && asc === true) {
              // If so, mark as a switch and break the loop:
              shouldSwitch = true;
              break;
            }
          if (Number(x.innerHTML) < Number(y.innerHTML) && asc === false) {
                // If so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
      }else {
          if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase() && asc === true) {
              // If so, mark as a switch and break the loop:
              shouldSwitch = true;
              break;
            }
          if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase() && asc === false) {
                // If so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
      }
      
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      allRows[i].parentNode.insertBefore(allRows[i + 1], allRows[i]);
      switching = true;
    }
  }
}
