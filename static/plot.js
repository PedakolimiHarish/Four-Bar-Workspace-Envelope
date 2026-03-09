let frames = [];
let animationIndex = 0;
let animationTimer = null;


function playAnimation() {

    if (!frames.length) return;

    if (animationTimer !== null) return; // already playing

    animationTimer = setInterval(() => {

        Plotly.animate("plot", frames[animationIndex], {
            frame: { duration: 0, redraw: true },
            transition: { duration: 0 }
        });

        animationIndex++;

        if (animationIndex >= frames.length) {
            animationIndex = 0; // loop
        }

    }, 40);
}

function showError(message) {
    const errorBox = document.getElementById("error-box");
    errorBox.innerText = message;
    errorBox.style.display = "block";

    // Clear plot
    Plotly.purge("plot");
}

function pauseAnimation() {

    if (animationTimer !== null) {
        clearInterval(animationTimer);
        animationTimer = null;
    }
}


async function runAnimation() {

    // Clear previous error
    const errorBox = document.getElementById("error-box");
    errorBox.style.display = "none";

    const params = {
        L1: parseFloat(document.getElementById("L1").value),
        L2: parseFloat(document.getElementById("L2").value),
        L3: parseFloat(document.getElementById("L3").value),
        L4: parseFloat(document.getElementById("L4").value),
        driver: parseInt(document.getElementById("driver").value)
    };

    const response = await fetch("/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params)
    });

    const data = await response.json();

    if (!data.success) {

        if (data.properties) {
            document.getElementById("assembly").innerText =
                data.properties["Assembly"] || "-";
        }

        showError(data.error);
        return;
    }

    if (data.change_point) {
        showError("Change-point mechanism: singular toggle configuration detected. Motion may exhibit branch merging.");
    }

    console.log("Linkage Properties:", data.properties);

    // Update UI
    if (data.properties) {

        document.getElementById("assembly").innerText =
            data.properties["Assembly"] || "-";

        document.getElementById("grashof-class").innerText =
            data.properties["Grashof Class"] || "-";

        document.getElementById("mechanism-type").innerText =
            data.properties["Mechanism Type"] || "-";

        document.getElementById("input-type").innerText =
            data.properties["Input Type"] || "-";

        document.getElementById("output-type").innerText =
            data.properties["Output Type"] || "-";

        document.getElementById("workspace-area").innerText =
            (data.properties["Workspace Area"] ?? "-") + " units²";
    }
    frames = [];
    animationIndex = 0;

    // -----------------------------
    // Compute bounds for centering
    // -----------------------------
    const allX = [];
    const allY = [];

    data.A.forEach(p => { allX.push(p[0]); allY.push(p[1]); });
    data.B.forEach(p => { allX.push(p[0]); allY.push(p[1]); });
    data.C.forEach(p => { allX.push(p[0]); allY.push(p[1]); });
    data.D.forEach(p => { allX.push(p[0]); allY.push(p[1]); });

    const xmin = Math.min(...allX);
    const xmax = Math.max(...allX);
    const ymin = Math.min(...allY);
    const ymax = Math.max(...allY);

    const padding = 0.2 * Math.max(xmax - xmin, ymax - ymin);

    const xRange = [xmin - padding, xmax + padding];
    const yRange = [ymin - padding, ymax + padding];

    // -----------------------------
    // Build animation frames
    // -----------------------------
    for (let i = 0; i < data.A.length; i++) {

        frames.push({
            data: [
                // Four-bar linkage
                {
                    x: [
                        data.A[i][0], data.B[i][0],
                        data.C[i][0], data.D[i][0],
                        data.A[i][0]
                    ],
                    y: [
                        data.A[i][1], data.B[i][1],
                        data.C[i][1], data.D[i][1],
                        data.A[i][1]
                    ],
                    mode: "lines+markers",
                    line: { width: 3 },
                    marker: { size: 8 },
                },

                // Joint labels
                {
                    x: [
                        data.A[i][0], data.B[i][0],
                        data.C[i][0], data.D[i][0]
                    ],
                    y: [
                        data.A[i][1], data.B[i][1],
                        data.C[i][1], data.D[i][1]
                    ],
                    mode: "text",
                    text: ["A", "B", "C", "D"],
                    textposition: "top center",
                    showlegend: false
                },

                // Workspace trail (output link point C)
                {
                    x: data.C.slice(0, i + 1).map(p => p[0]),
                    y: data.C.slice(0, i + 1).map(p => p[1]),
                    mode: "lines",
                    line: { width: 2, dash: "dot" },
                    name: "Workspace"
                }
            ]
        });
    }

    // -----------------------------
    // Initial plot
    // -----------------------------
    // Compute center
    const cx = 0.5 * (xmin + xmax);
    const cy = 0.5 * (ymin + ymax);

    // Use the larger span to keep plot square
    const span = Math.max(xmax - xmin, ymax - ymin) * 0.6;

    Plotly.newPlot("plot", frames[0].data, {
        xaxis: {
            range: [cx - span, cx + span],
            zeroline: true,
            zerolinewidth: 2,
            zerolinecolor: "black",
            scaleanchor: "y"
        },
        yaxis: {
            range: [cy - span, cy + span],
            zeroline: true,
            zerolinewidth: 2,
            zerolinecolor: "black"
        },
        showlegend: false,
        margin: { l: 40, r: 40, t: 20, b: 40 }
    });

}