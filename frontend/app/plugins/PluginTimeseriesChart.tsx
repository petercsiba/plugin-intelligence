// Whoa, this fixes "Super expression must either be null or a function" error!
"use client"

import React from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {PluginTimeseriesData} from "./models";
import {formatCurrency, formatNumber, formatNumberShort} from "@/utils";

interface Props {
    data: PluginTimeseriesData[];
}

interface CustomTooltipProps {
    active?: boolean;
    payload?: Array<{
        payload: PluginTimeseriesData;
    }>;
    label?: string;
}


const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
    if (active && payload && payload.length) {
        const data: PluginTimeseriesData = payload[0].payload;

        return (
            <div className="custom-tooltip">
                <strong>{`${data.p_date}`}</strong>
                <ul>
                    <li>{`Downloads: ${formatNumber(data.user_count)}`}</li>
                    <li>{`Average Rating: ${formatNumber(data.avg_rating)}`}</li>
                    <li>{`Rating Count: ${formatNumber(data.rating_count)}`}</li>
                </ul>
            </div>
        );
    }

    return null;
};

const PluginTimeseriesChart: React.FC<Props> = ({data}) => {
    const formattedData = data.map(item => ({
        ...item,
        avg_rating: item.avg_rating ?? null,
        rating_count: item.rating_count ?? null,
    }));
    console.log("formattedData", formattedData)

    const ratingTicks = [0, 1, 2, 3, 4, 5];

    return (
        <ResponsiveContainer width="100%" height={400}>
            <LineChart
                data={formattedData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="p_date" />
                <YAxis yAxisId="user_count_axis" domain={[0, 'dataMax']} stroke="#8884d8" tickFormatter={(value) => formatNumberShort(value)} />
                <YAxis yAxisId="rating_count_axis" orientation="right" domain={[0, 'dataMax']} stroke="#82ca9d" />
                <YAxis yAxisId="avg_rating_axis" orientation="right" domain={[0, 5]} stroke="#ffc658" ticks={ratingTicks} />

                <Tooltip content={<CustomTooltip />} />
                <Legend />

                {/*TODO(P1, ux): Add nicer labels */}
                <Line type="monotone" dataKey="user_count" stroke="#8884d8" yAxisId="user_count_axis" />
                <Line type="monotone" dataKey="rating_count" stroke="#82ca9d" yAxisId="rating_count_axis" />
                <Line type="monotone" dataKey="avg_rating" stroke="#ffc658" yAxisId="avg_rating_axis" />
            </LineChart>
        </ResponsiveContainer>
    );
};
export default PluginTimeseriesChart;
