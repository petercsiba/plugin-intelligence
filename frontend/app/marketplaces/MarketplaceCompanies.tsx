// Mark the file as a Client Component
"use client";

import * as React from 'react';
import { useState, useEffect } from 'react';
import Container from '@mui/material/Container';
import {CompaniesTopResponse} from "../companies/models";
import PageLoading from "@/components/PageLoading";
import NoResultsFound from "@/components/NoResultsFound";
import PageTitle from "@/components/PageTitle";
import { fetchTopCompanies } from '../companies/driver';
import TopCompaniesBubbleChart from "../companies/TopCompaniesBubbleChart";
import CompaniesTable from "../companies/CompaniesTable";
import {MarketplaceName} from "./models";
import { Typography } from '@mui/material';
import SubPageTitle from "@/components/SubPageTitle";

interface MarketplaceCompaniesProps {
  marketplaceName: MarketplaceName;
}

const MarketplaceCompanies: React.FC<MarketplaceCompaniesProps> = ({ marketplaceName }) => {
    const [loading, setLoading] = useState(true);
    const [companies, setCompanies] = useState<CompaniesTopResponse[]>([]);

    useEffect(() => {
        console.log("useEffect is being triggered");
        (async () => {
            try {
                const fetchedCompanies = await fetchTopCompanies(marketplaceName);
                setCompanies(fetchedCompanies);
            } catch (error) {
                console.error('Error fetching companies:', error);
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    if (loading) return <PageLoading />;

    if (companies.length === 0) return <NoResultsFound model_name={"Companies"} />;

    return (
        <Container maxWidth="lg">
            <SubPageTitle title={`Top ${companies.length} ${marketplaceName} Developers by Cumulative Downloads`} />
            <TopCompaniesBubbleChart marketplaceName={marketplaceName}  />
            <CompaniesTable companies={companies} />
        </Container>
    );
}

export default MarketplaceCompanies;