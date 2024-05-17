// pages/BubbleChart.js
import React, {useEffect, useState } from 'react';
import { ScatterChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid, Scatter, ResponsiveContainer, Label } from 'recharts';
import NextLink from 'next/link';
import Box from '@mui/material/Box';
import * as d3 from 'd3-scale';
import {formatNumber, formatNumberShort} from "@/utils";
import { scaleLog } from 'd3-scale';
import {CompaniesTopResponse} from "./models";
import {fetchTopCompanies} from "./driver";
import {MarketplaceName} from "../marketplaces/models";

// There is somewhat few plugins with below 3.0 rating; and 3.0 is itself quite low so lets just do red there.
const MIN_RATING = 3.0;
const TOP_RATING = 5.0;
const TOP_RATING_COLOR = '#4caf50'; // Green


interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: CompaniesTopResponse;
  }>;
  label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;

    return (
        // TODO(P0, no <p> in <div>): Use a list or a table for better semantics
        <div className="custom-tooltip" style={{backgroundColor: "#fff", padding: "10px", border: "1px solid #ccc"}}>
            <strong>{data.display_name}</strong>
            <ul>
                <li>{`Plugin Count: ${data.count_plugin}`}</li>
                <li className="label">{`Total Downloads: ${formatNumberShort(data.sum_download_count)}`}</li>
                <li>{`Average Rating: ${data.avg_avg_rating}`}</li>
            </ul>
        </div>
    );
  }

    return null;
};

interface TopCompaniesBubbleChartProps {
    marketplaceName: MarketplaceName;
}

const TopCompaniesBubbleChart: React.FC<TopCompaniesBubbleChartProps> = ({ marketplaceName }) => {
  const [data, setBubbleData] = useState<CompaniesTopResponse[]>([]);

  const fetchBubbleData = async () => {
    try {
      setBubbleData(await fetchTopCompanies(marketplaceName));
    } catch (error) {
      console.error('Error fetching bubble data:', error);
    }
  };

  useEffect(() => {
    fetchBubbleData();
  }, [marketplaceName]); // Add fetchBubbleData and marketplaceName as dependencies

  // Color scale function using d3-scale
  const ratingColorScale = d3.scaleLinear()
    .domain([MIN_RATING, 4, 4.8, TOP_RATING])
      // Ignore TypeScript checking for `.range()` as it returns a string array
      //     Red (#f44336): For the lowest ratings (Material Design Red 500).
      //     Yellow (#FFEB3B): Midpoint yellow (Material Design Yellow 400).
      //     Green (#4caf50): For higher ratings (Material Design Green 500).
      // @ts-ignore
    .range(['#f44336', '#FFEB3B', TOP_RATING_COLOR, TOP_RATING_COLOR]);

  // const logTicks = [1000, 10000, 100000, 1000000, 10000000, 100000000];

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
          <XAxis type="number" dataKey="sum_download_count" scale={scaleLog().base(10)} domain={['dataMin', 'dataMax']} name="Downloads" tickFormatter={(value) => formatNumber(value)}>
            <Label value="Downloads (log10)" offset={-10} position="insideBottomRight" style={{ color: 'black', fontWeight: 'bold' }} />
          </XAxis>
          <YAxis type="number" dataKey="count_plugin" scale={scaleLog().base(2)} domain={[1, 'dataMax']} name="Plugin Count">
              <Label value="Plugin Count (log2)" offset={11} position="insideTopLeft" style={{ color: 'black', fontWeight: 'bold'}} />
          </YAxis>
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: "3 3" }} />
                <Legend
        payload={[
          { value: 'Revenue Estimate (Size)', type: 'circle', color: '#8884d8' }, // TODO: (actually calculate this)
          { value: 'Average Rating (Color)', type: 'circle', color: TOP_RATING_COLOR },
        ]}
      />
          <Scatter
            name="Plugin Developed to Downloads; Size is Revenue Estimate; Color is Average Rating"
            data={data}
            fill="#8884d8"
            shape={(props: { cx?: any; cy?: any; payload?: CompaniesTopResponse; }) => {
              const { payload } = props;

              // @ts-ignore - payload is possibly undefined
              // let radius = Math.sqrt(payload.revenue_estimate) / 150
              // radius = Math.max(5, Math.min(50, radius));
              let radius = 20
              // revenue = (150 * r)^2; so the maximum display is (50 * 150) ^ 2 = $11,250,000

              // @ts-ignore
              const avg_rating = Math.max(MIN_RATING, payload?.avg_avg_rating);

              return (
                  // @ts-ignore - payload is possibly undefined
                    <NextLink href={`/companies/${payload?.slug}/detail`} passHref>
                    <circle
                      cx={props.cx}
                      cy={props.cy}
                      r={radius}
                      // @ts-ignore (this somehow just works)
                      fill={ratingColorScale(avg_rating)}
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

export default TopCompaniesBubbleChart;
