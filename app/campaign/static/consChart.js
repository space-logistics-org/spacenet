var wm = 0;
var fm = 0;
var gm = 0;
var him = 0;
var cm = 0;
var pim = 0;
var wmass = 0;
var fmass = 0;
var gmass = 0;
var himass = 0;
var cmass = 0;
var pimass = 0;

function onload() {
  var tableRef = document.getElementById('elementTableBody');
  var tableRows = tableRef.rows;
  var checkedRows = [];
  for (var i = 0; i < tableRows.length; i++) {
    ty = tableRows[i].cells[3].innerText;
    if ty == "Water and Support Equipment" {
      wm = Number(tableRows[i].cells[6].innerText);
      wmass = Number(masses + m);
    }
    if ty == "Food and Support Equipment" {
      fm = Number(tableRows[i].cells[6].innerText);
      fmass = Number(masses + m);
    }
    if ty == "Gases" {
      gm = Number(tableRows[i].cells[6].innerText);
      gmass = Number(masses + m);
    }
    if ty == "Hygiene Items" {
      him = Number(tableRows[i].cells[6].innerText);
      himass = Number(masses + m);
    }
    if ty == "Clothing" {
      cm = Number(tableRows[i].cells[6].innerText);
      cmass = Number(masses + m);
    }
    if ty == "Personal Items" {
      pim = Number(tableRows[i].cells[6].innerText);
      pimass = Number(masses + m);
    }
}
