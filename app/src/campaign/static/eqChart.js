var om = 0;
var evam = 0;
var hm = 0;
var sm = 0;
var comum = 0;
var compm = 0;
var tbm = 0;
var wam = 0;
var cmm = 0;
var omass = 0;
var evamass = 0;
var hmass = 0;
var smass = 0;
var comumass = 0;
var compmass = 0;
var tbmass = 0;
var wamass = 0;
var cmmass = 0;

function onload() {
  var tableRef = document.getElementById('elementTableBody');
  var tableRows = tableRef.rows;
  var checkedRows = [];
  for (var i = 0; i < tableRows.length; i++) {
    ty = tableRows[i].cells[3].innerText;
    if ty == "Office Equipment and Supplies" {
      om = Number(tableRows[i].cells[6].innerText);
      omass = Number(masses + m);
    }
    if ty == "EVA Equipment and Consumables" {
      evam = Number(tableRows[i].cells[6].innerText);
      evamass = Number(masses + m);
    }
    if ty == "Health Equipment and Consumables" {
      hm = Number(tableRows[i].cells[6].innerText);
      hmass = Number(masses + m);
    }
    if ty == "Safety Equipment" {
      sm = Number(tableRows[i].cells[6].innerText);
      smass = Number(masses + m);
    }
    if ty == "Communications Equipment" {
      comum = Number(tableRows[i].cells[6].innerText);
      comumass = Number(masses + m);
    }
    if ty == "Computers and Support Equipment" {
      pim = Number(tableRows[i].cells[6].innerText);
      pimass = Number(masses + m);
    }
    //Something not correct here? Classification?
    if ty == "Waste" {
      tbm = Number(tableRows[i].cells[6].innerText);
      tbmass = Number(masses + m);
    }
    if ty == "Waste Management Equipment" {
      wam = Number(tableRows[i].cells[6].innerText);
      wamass = Number(masses + m);
    }
    ety = tableRows[i].cells[2].innerText;
    if ty == "Human Agent" {
      cmm = Number(tableRows[i].cells[6].innerText);
      cmmass = Number(masses + m);
    }

}
