async function runAnimation() {

    const params = {
        L1: parseFloat(document.getElementById("L1").value),
        L2: parseFloat(document.getElementById("L2").value),
        L3: parseFloat(document.getElementById("L3").value),
        L4: parseFloat(document.getElementById("L4").value)
    };

    const response = await fetch("/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params)
    });

    const data = await response.json();

    const frames = [];

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


    // -----------------------------
    // Animate continuously
    // -----------------------------
    function animateLoop() {
        Plotly.animate("plot", frames, {
            frame: { duration: 40, redraw: true },
            transition: { duration: 0 },
            mode: "afterall"
        }).then(() => {
            animateLoop();  // restart animation
        });
    }

    animateLoop();

}