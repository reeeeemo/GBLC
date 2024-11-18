import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import styles from './page.module.css';

const BondPredictionChart = ({ predictions, future_dates, inflation }) => {
    if (!predictions || !predictions[0] || !predictions[0][1]) {
        return null;
    }

    const transform_data = () => {
        const data_len = predictions[0][1].length;
        const bondsPerYear = 12;
        
        const chartData = [];

        for (let i = 0; i < data_len; i++) {
            const yearPoint = i / bondsPerYear;

            const inflation_rate = inflation && i < inflation.length ? inflation[i] : 0;

            const short_real = predictions[0][1][i] - inflation_rate;
            const med_real = predictions[1][1][i] - inflation_rate;
            const long_real = predictions[2][1][i] - inflation_rate;

            const dataPoint = {
                year: yearPoint,
                short: Number(predictions[0][1][i].toFixed(2)),
                med: Number(predictions[1][1][i].toFixed(2)),
                long: Number(predictions[2][1][i].toFixed(2)),
                short_real: Number(short_real.toFixed(2)),
                med_real: Number(med_real.toFixed(2)),
                long_real: Number(long_real.toFixed(2)),
                inflation: inflation && i < inflation.length ?
                    Number(inflation[i].toFixed(2)) : null
            };
            chartData.push(dataPoint);
        }
        return chartData;
    };

    const chartData = transform_data();

    // Calculate min and max values for Y axis
    const allValues = chartData.flatMap(point => 
        [point.short, point.med, point.long, point.short_real, point.med_real, point.long_real, point.inflation]
            .filter(val => val !== null)
    );
    const minValue = Math.floor(Math.min(...allValues));
    const maxValue = Math.ceil(Math.max(...allValues));

    const maxYear = Math.ceil(chartData[chartData.length - 1].year);

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
                data={chartData}
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
                    formatter={(value) => [`${value}%`, 'Rate']}
                    labelFormatter={formatTooltipLabel}
                />
                <Legend
                    verticalAlign='top'
                />
                <Line
                    type="monotone"
                    dataKey="short_real"
                    stroke="#8884d8"
                    name="Short Term"
                    dot={false}
                />
                <Line
                    type="monotone"
                    dataKey="med_real"
                    stroke="#82ca9d"
                    name="Medium Term"
                    dot={false}
                />
                <Line
                    type="monotone"
                    dataKey="long_real"
                    stroke="#ffc658"
                    name="Long Term"
                    dot={false}
                />

            </LineChart>
        </div>
    );
};

export default BondPredictionChart;