// pages/BubbleChart.js
import React, {useEffect, useState } from 'react';
import { ScatterChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid, Scatter, ResponsiveContainer } from 'recharts';
import NextLink from 'next/link';
import Box from '@mui/material/Box';
import * as d3 from 'd3-scale';

const baseUrl = process.env.NEXT_PUBLIC_API_URL
// There is somewhat few plugins with below 3.0 rating; and 3.0 is itself quite low so lets just do red there.
const MIN_RATING = 3.0;

// Define the shape of a bubble data object
interface BubbleData {
  id: string;
  name: string;

  user_count: number;
  rating: number;  // float
  revenue_estimate: number;
  arpu_cents: number;
}

const ArpuBubbleChartComponent = () => {
    // State to store the fetched data with BubbleData type
    const [data, setBubbleData] = useState<BubbleData[]>([]);

    // Function to fetch bubble data from an API
    const fetchBubbleData = async () => {
      try {
        const response = await fetch(`${baseUrl}/charts/arpu-bubble`);
        const data: BubbleData[] = await response.json(); // Type the response explicitly
        setBubbleData(data);
      } catch (error) {
        console.error('Error fetching bubble data:', error);
      }
    };

    // Fetch data when the component mounts
    useEffect(() => {
      fetchBubbleData();
    }, []);


  // Color scale function using d3-scale
  // TODO(P0, ux): Maybe better is to just
  const colorScale = d3.scaleLinear()
    .domain([MIN_RATING, 5])
      // Ignore TypeScript checking for `.range()` as it returns a string array
      // @ts-ignore
    .range(['red', 'green']);

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center', // Centers content horizontally
        alignItems: 'center', // Optional: vertically centers content if height is also set
        height: '40vh',
        padding: '16px'
      }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid />
          <XAxis type="number" dataKey="user_count" name="Users" unit=" users" />
          <YAxis type="number" dataKey="arpu_cents" name="ARPU" unit="¢" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Legend />
          <Scatter
            name="Bubble Size: Revenue Estimate, Bubble Color: Rating"
            data={data}
            fill="#8884d8"
            shape={(props: { cx?: any; cy?: any; payload?: BubbleData; }) => {
              const { payload } = props;

              // @ts-ignore - payload is possibly undefined
              let radius = Math.sqrt(payload.revenue_estimate) / 150
              radius = Math.max(5, Math.min(50, radius));
              // revenue = (150 * r)^2; so the maximum display is (50 * 150) ^ 2 = $11,250,000

              // @ts-ignore
              const rating = Math.max(MIN_RATING, payload.rating);

              return (
                  // @ts-ignore - payload is possibly undefined
                    <NextLink href={`/plugin/${payload.id}`} passHref>
                    <circle
                      cx={props.cx}
                      cy={props.cy}
                      r={radius}
                      fill={colorScale(rating)}
                      stroke="black"
                    />
                </NextLink>
              );
            }}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ArpuBubbleChartComponent;
