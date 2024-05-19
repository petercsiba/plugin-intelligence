// pages/BubbleChart.js
import React, {useEffect, useState } from 'react';
import { ScatterChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid, Scatter, ResponsiveContainer, Label } from 'recharts';
import NextLink from 'next/link';
import Box from '@mui/material/Box';
import * as d3 from 'd3-scale';
import {formatCurrency, formatNumber, formatNumberShort} from "@/utils";
import { scaleLog } from 'd3-scale';
import {MarketplaceName} from "../marketplaces/models";

const baseUrl = process.env.NEXT_PUBLIC_API_URL
// There is somewhat few plugins with below 3.0 rating; and 3.0 is itself quite low so lets just do red there.
const MIN_RATING = 3.0;
const TOP_RATING = 5.0;
const TOP_RATING_COLOR = '#4caf50'; // Green

// Define the shape of a bubble data object
interface BubbleData {
  id: string;
  name: string;

  user_count: number;
  user_count_thousands: number;
  avg_rating: number;  // float
  revenue_estimate: number;
  arpu_cents: number;
  arpu_dollars: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: BubbleData;
  }>;
  label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;

    return (
        <div className="custom-tooltip" style={{backgroundColor: "#fff", padding: "10px", border: "1px solid #ccc"}}>
            <strong>{data.name}</strong>
            <ul>
                <li className="label">{`Downloads: ${formatNumberShort(data.user_count)}`}</li>
                <li>{`ARPU: ${formatCurrency(data.arpu_dollars)}`}</li>
                <li>{`Average Rating: ${formatNumber(data.avg_rating)}`}</li>
                <li>{`Revenue*: ${formatCurrency(data.revenue_estimate)}`}</li>
            </ul>
        </div>
    );
  }

    return null;
};


interface ArpuBubbleChartComponentProps {
    marketplaceName: MarketplaceName;
}

const ArpuBubbleChartComponent: React.FC<ArpuBubbleChartComponentProps> = ({ marketplaceName }) => {
    // State to store the fetched data with BubbleData type
    const [data, setBubbleData] = useState<BubbleData[]>([]);

    // Function to fetch bubble data from an API
    const fetchBubbleData = async () => {
      try {
        const response = await fetch(`${baseUrl}/charts/plugins-arpu-bubble?marketplace_name=${marketplaceName}`);
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
    .domain([MIN_RATING, 4, 4.8, TOP_RATING])
      // Ignore TypeScript checking for `.range()` as it returns a string array
      //     Red (#f44336): For the lowest ratings (Material Design Red 500).
      //     Yellow (#FFEB3B): Midpoint yellow (Material Design Yellow 400).
      //     Green (#4caf50): For higher ratings (Material Design Green 500).
      // @ts-ignore
    .range(['#f44336', '#FFEB3B', TOP_RATING_COLOR, TOP_RATING_COLOR]);

  const logTicks = [1000, 10000, 100000, 1000000, 10000000, 100000000];

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
          <XAxis type="number" scale={scaleLog().base(10)} domain={[1000, 100000000]} dataKey="user_count" name="Users" ticks={logTicks} tickFormatter={(value) => formatNumber(value)}>
            <Label value="Downloads" offset={-10} position="insideBottomRight" style={{ color: 'black', fontWeight: 'bold' }} />
          </XAxis>
          <YAxis type="number" dataKey="arpu_dollars" name="ARPU" tickFormatter={(value) => formatCurrency(value)}>
              <Label value="ARPU" offset={11} position="insideTopLeft" style={{ color: 'black', fontWeight: 'bold'}} />
          </YAxis>
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: "3 3" }} />
                <Legend
        payload={[
          { value: 'Revenue Estimate (Size)', type: 'circle', color: '#8884d8' },
          { value: 'Average Rating (Color)', type: 'circle', color: TOP_RATING_COLOR },
        ]}
      />
          <Scatter
            name="Estimated ARPU to Downloads; Size is Revenue Estimate; Color is Average Rating"
            data={data}
            fill="#8884d8"
            shape={(props: { cx?: any; cy?: any; payload?: BubbleData; }) => {
              const { payload } = props;

              // @ts-ignore - payload is possibly undefined
              let radius = Math.sqrt(payload.revenue_estimate) / 150
              radius = Math.max(5, Math.min(50, radius));
              // revenue = (150 * r)^2; so the maximum display is (50 * 150) ^ 2 = $11,250,000

              // @ts-ignore
              const avg_rating = Math.max(MIN_RATING, payload?.avg_rating);

              return (
                  // @ts-ignore - payload is possibly undefined
                    <NextLink href={`/plugins/${payload.id}`} passHref>
                    <circle
                      cx={props.cx}
                      cy={props.cy}
                      r={radius}
                      // @ts-ignore (this somehow just works)
                      fill={colorScale(avg_rating)}
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
