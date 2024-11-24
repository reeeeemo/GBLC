import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import styles from './page.module.css';

const BondPredictionChart = ({ predictions, best_route }) => {
    if (!predictions || !predictions[0]) { // if predictions aren't there, best_route won't be either
        return null;
    }

    const bestRouteData = predictions.map(pred => {
        const bestRoutePoint = best_route.find(point => point[0] == pred.year);
        return {
            year: pred.year,
            value: bestRoutePoint ? pred[bestRoutePoint[1]] : null
        };
    });

    // Calculate min and max values for Y axis
    const allValues = predictions.flatMap(point => 
        [point.short, point.med, point.long, point.inflation]
            .filter(val => val !== null)
    );
    const minValue = Math.floor(Math.min(...allValues));
    const maxValue = Math.ceil(Math.max(...allValues));

    const maxYear = Math.ceil(predictions[predictions.length - 1].year);

    const formatXAxis = (value) => {
        if (Number.isInteger(value)) {
            return `${value}`;
        }
        return '';  // no non-int years
    };

    // Generate ticks for every 5 years
    const generateTicks = () => {
        const ticks = [];
        for (let i = 0; i <= maxYear; i += 5) {
            ticks.push(i);
        }
        return ticks;
    };

    const formatTooltipLabel = (value) => {
        return `Year ${Math.round(value)}`;
    };

    return (
        <div className={styles.calculator}>
            <h1 style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                marginBottom: '1.5rem',
                textAlign: 'center'
            }}>
                Rate of Return (Inflation-Reduced)
            </h1>
            <LineChart
                width={600}
                height={300}
                data={predictions}
                margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 20,
                }}
            >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                    dataKey="year"
                    label={{ value: 'Years', position: 'bottom'}}
                    tickFormatter={formatXAxis}
                    ticks={generateTicks()}
                    domain={[0, maxYear]}
                />
                <YAxis
                    label={{ value: 'Rate (%)', angle: -90, position: 'left' }}
                    domain={[minValue, maxValue]}
                    tickFormatter={(value) => `${value}%`}
                />
                <Tooltip
                    formatter={(value) => [`${value.toFixed(2)}%`, 'Rate']}
                    labelFormatter={formatTooltipLabel}
                />
                <Legend
                    verticalAlign='top'
                />
                <Line
                    type="monotone"
                    dataKey="short"
                    stroke="#8884d8"
                    name="Short Term"
                    dot={false}
                    strokeWidth={2}
                />
                <Line
                    type="monotone"
                    dataKey="med"
                    stroke="#82ca9d"
                    name="Medium Term"
                    dot={false}
                    strokeWidth={2}
                />
                <Line
                    type="monotone"
                    dataKey="long"
                    stroke="#ffc658"
                    name="Long Term"
                    dot={false}
                    strokeWidth={2}
                />
                <Line
                    type="monotone"
                    data={bestRouteData}
                    dataKey="value"
                    stroke="#ff0000"
                    name="Your Return"
                    dot={false}
                    strokeWidth={1}
                    connectNulls={true}
                />
            </LineChart>
        </div>
    );
};

export default BondPredictionChart;