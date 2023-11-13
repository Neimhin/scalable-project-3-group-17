// Example matrix data
console.log("d3_matrix.js")
const matrixData = [
    [0, 0.5, 1],
    [0.8, 0.3, 0.1],
    [0.2, 0.7, 0.5]
];

// Function to map values to colors
function valueToColor(value) {
    const colorScale = d3.scaleLinear()
        .domain([0, 1])
        .range(["white", "black"]);
    return colorScale(value);
}

// Select the container and append divs for each row
const div = d3.select("#matrix")
  .selectAll(".grid-row")
  .data(matrixData)
  .enter()
  .append("div")
  .attr("class", "grid-row")


// Append divs for each cell in the row
div.selectAll(".grid-cell")
    .data(d => d)
    .enter().append("div")
    .attr("class", "grid-cell")
    .style("background-color", d => valueToColor(d));
