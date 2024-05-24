// Whoa, this fixes "Super expression must either be null or a function" error!
"use client"

import React from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {PluginTimeseriesData} from "./models";
import {formatNumber, formatNumberShort} from "@/utils";
import { format, differenceInDays, differenceInYears } from 'date-fns';

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

        // Convert the Unix timestamp back to a date string
        const date = new Date(data.p_date);
        const formattedDate = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;

        return (
            <div className="custom-tooltip">
                <strong>{formattedDate}</strong>
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

const formatDateTick = (tick: string, data: PluginTimeseriesData[]) => {
    const firstDate = new Date(data[0].p_date);
    const lastDate = new Date(data[data.length - 1].p_date);

    const daysDiff = differenceInDays(lastDate, firstDate);
    const yearsDiff = differenceInYears(lastDate, firstDate);

    // TODO(P2, ux): The chart overflows a bit on the right side, maybe we should add some padding to the right
    if (yearsDiff > 2) {
        // More than a year;
        return format(new Date(tick), 'yyyy/MM');
    } else if (daysDiff > 30) {
        // More than a month but less than a year
        return format(new Date(tick), 'yyyy/MM');
    } else {
        // Less than a month
        return format(new Date(tick), 'yyyy-MM-dd');
    }
};


const PluginTimeseriesChart: React.FC<Props> = ({data}) => {
    const formattedData = data.map(item => ({
        ...item,
        avg_rating: item.avg_rating ?? null,
        rating_count: item.rating_count ?? null,
        p_date: new Date(item.p_date).getTime(),
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
                <XAxis
                    dataKey="p_date"
                    scale="time"
                    domain={['dataMin', 'dataMax']}
                    tickFormatter={(tick) => formatDateTick(tick, data)}
                />
                <YAxis yAxisId="user_count_axis" domain={[0, 'dataMax']} stroke="#8884d8" tickFormatter={(value) => formatNumberShort(value)} />
                <YAxis yAxisId="rating_count_axis" orientation="right" domain={[0, 'dataMax']} stroke="#82ca9d" />
                <YAxis yAxisId="avg_rating_axis" orientation="right" domain={[0, 5]} stroke="#ffc658" ticks={ratingTicks} />

                <Tooltip content={<CustomTooltip />} />
                <Legend formatter={(value) => {
                    const labels: Record<string, string> = {
                        user_count: 'Downloads',
                        rating_count: 'Rating Count',
                        avg_rating: 'Average Rating',
                    };
                    return labels[value] || value;
                }} />

                {/*TODO(P1, ux): Add nicer labels */}
                <Line type="monotone" dataKey="user_count" stroke="#8884d8" yAxisId="user_count_axis" />
                <Line type="monotone" dataKey="rating_count" stroke="#82ca9d" yAxisId="rating_count_axis" />
                <Line type="monotone" dataKey="avg_rating" stroke="#ffc658" yAxisId="avg_rating_axis" />
            </LineChart>
        </ResponsiveContainer>
    );
};
export default PluginTimeseriesChart;
