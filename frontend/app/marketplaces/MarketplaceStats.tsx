"use client";
import React, { useEffect, useState } from 'react';
import {MarketplaceName, MarketplaceStatsResponse} from "./models";
import {formatCurrency, formatNumber, formatNumberShort} from "@/utils";


const baseUrl = process.env.NEXT_PUBLIC_API_URL

interface MarketplaceStatsProps {
    marketplaceName: MarketplaceName;
}

const MarketplaceStats: React.FC<MarketplaceStatsProps> = ({ marketplaceName }) => {
    const [marketplaceStats, setMarketplaceStats] = useState<MarketplaceStatsResponse | null>(null);

    useEffect(() => {
        async function fetchData() {
            try {
                const response = await fetch(`${baseUrl}/charts/marketplace-stats?marketplace_name=${marketplaceName}`);
                const data: MarketplaceStatsResponse = await response.json();
                setMarketplaceStats(data);
            } catch (error) {
                console.error('Error fetching plugin stats:', error);
            }
        }

        fetchData();
    }, [marketplaceName, baseUrl]);

    return (
        <>
            {marketplaceStats ? (
                <ul>
                    <li>Number of Plugins: <strong>{formatNumber(marketplaceStats.total_plugins)}</strong></li>
                    <li>Total Downloads: <strong>{formatNumberShort(marketplaceStats.total_downloads)}</strong></li>
                    <li>Total Ratings: <strong>{formatNumberShort(marketplaceStats.total_ratings)}</strong></li>
                    <li>Average Downloads per
                        Plugin: <strong>{formatNumberShort(marketplaceStats.avg_downloads)}</strong></li>
                    <li>Average Rating (Weighted): <strong>{formatNumber(marketplaceStats.weighted_avg_rating)}</strong></li>
                    <li>Median Monthly Paid Tier: <strong>{formatCurrency(marketplaceStats.median_lowest_paid_tier)}</strong></li>
                    <li>Propensity to rate: <strong>{formatNumber(marketplaceStats.propensity_to_rate)} ratings / 1000 downloads </strong></li>
                </ul>

            ) : (
                <p>Loading data...</p>
            )}
        </>
    );
}

export default MarketplaceStats;
