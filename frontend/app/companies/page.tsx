// Mark the file as a Client Component
"use client";

import * as React from 'react';
import { useState, useEffect } from 'react';
import Container from '@mui/material/Container';
import NextLink from "next/link";
import Button from '@mui/material/Button';
import {CompaniesTopResponse} from "./models";
import {formatNumber, formatNumberShort} from "@/utils";
import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import PageLoading from "@/components/PageLoading";
import NoResultsFound from "@/components/NoResultsFound";
import PageTitle from "@/components/PageTitle";
import { fetchTopCompanies } from './driver';
import TopCompaniesBubbleChart from "./TopCompaniesBubbleChart";


export default function HomePage() {
    const [loading, setLoading] = useState(true);
    const [companies, setCompanies] = useState<CompaniesTopResponse[]>([]);

    useEffect(() => {
        console.log("useEffect is being triggered");
        (async () => {
            try {
                const fetchedCompanies = await fetchTopCompanies();
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
            <PageTitle title="Top Plugin Companies By Downloads" />
            <TopCompaniesBubbleChart />
            <TableContainer component={Paper}>
                <Table size="small"> {/* Smaller cell padding */}
                    <TableHead>
                        <TableRow>
                            <TableCell>Logo</TableCell>
                            <TableCell>Name</TableCell>
                            {/* TODO(P1, ux): Add tooltip what does this mean */}
                            <TableCell>Total Downloads</TableCell>
                            <TableCell>Plugin Count</TableCell>
                            <TableCell>Average Rating</TableCell>
                            <TableCell>Details</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {companies.map((company) => (
                            <TableRow key={company.slug}>
                                <TableCell>
                                    {company.img_logo_link ? (
                                        <img src={company.img_logo_link} alt={company.display_name} style={{ width: 48 }} />
                                    ) : (
                                        ''
                                    )}
                                </TableCell>
                                <TableCell style={{fontWeight: "bold"}}>{company.display_name}</TableCell>
                                <TableCell>{formatNumberShort(company.sum_download_count)}</TableCell>
                                <TableCell>{company.count_plugin}</TableCell>
                                <TableCell>{formatNumber(company.avg_avg_rating)}</TableCell>
                                <TableCell>
                                    <NextLink href={`/companies/${company.slug}/detail`} passHref>
                                        <Button variant="contained" color="primary" fullWidth> {/* Full width on mobile */}
                                            View
                                        </Button>
                                    </NextLink>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

        </Container>
    );
}
