// Mark the file as a Client Component
"use client";

import * as React from 'react';
import { useState, useEffect } from 'react';
import Container from '@mui/material/Container';
import {TopPluginResponse} from "./plugins/models";
import ArpuBubbleChartComponent from "./ArpuBubbleChart";
import PageLoading from "@/components/PageLoading";
import NoResultsFound from "@/components/NoResultsFound";
import PageTitle from "@/components/PageTitle";
import PluginTable from "./plugins/PluginTable";
import {fetchTopPlugins} from "./plugins/driver";

export default function HomePage() {
    const [loading, setLoading] = useState(true);
    const [plugins, setPlugins] = useState<TopPluginResponse[]>([]);

    useEffect(() => {
        console.log("useEffect is being triggered");
        (async () => {
            try {
                const fetchedPlugins = await fetchTopPlugins();
                setPlugins(fetchedPlugins);
            } catch (error) {
                console.error('Error fetching plugins:', error);
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    if (loading) return <PageLoading />;

    if (plugins.length === 0) return <NoResultsFound model_name={"Plugins"} />;

    return (
        <Container maxWidth="lg">
            <PageTitle title="Top Google Plugins By Estimated Revenue" />
            <ArpuBubbleChartComponent />
            <PluginTable plugins={plugins} />

        </Container>
    );
}
