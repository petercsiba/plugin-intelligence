import React from "react";
import {
    Container,
    Paper,
    Rating,
    Typography,
    List,
    ListItem,
    ListItemText,
} from "@mui/material";
import Box from "@mui/material/Box";
import {PluginDetailsResponse} from "../../models";
import ExternalLink from "@/components/ExternalLink";
import {fixThatArrayWithNullShit, formatCurrency, formatNumber} from "@/utils";
import dynamic from "next/dynamic";
import ListBoxOneLine from "@/components/ListBoxOneLine";
import NoResultsFound from "@/components/NoResultsFound";
import PluginTimeseriesChart from "../../PluginTimeseriesChart";
import {fetchPluginTimeseries} from "../../driver";

const BoxWithInnerHtml = dynamic(
    () => import('@/components/BoxWithInnerHtml'),
    { ssr: false }  // This will disable server-side rendering for the component
);

const baseUrl = process.env.NEXT_PUBLIC_API_URL

// Function to fetch plugins details
async function fetchPluginDetails(plugin_id: string): Promise<PluginDetailsResponse | null> {
    const response = await fetch(`${baseUrl}/plugins/${plugin_id}/details`, {
        cache: "no-store", // Adjust caching as needed
    });

    if (!response.ok) {
        console.error(`Error fetching plugin details: ${response.statusText}`);
        return null;
    }

    return await response.json();
}

export default async function PluginDetailsPage({ params }: { params: { plugin_id: string } }) {
    const plugin = await fetchPluginDetails(params.plugin_id);
    if (!plugin) return <NoResultsFound model_name={`Plugin with id "${params.plugin_id}"`} />;

    const timeseriesData = await fetchPluginTimeseries(params.plugin_id);

    // FIX SHIT
    const lower_bound = fixThatArrayWithNullShit(plugin.revenue_lower_bound)
    const upper_bound = fixThatArrayWithNullShit(plugin.revenue_upper_bound)
    const reviews_summary_html = fixThatArrayWithNullShit(plugin.reviews_summary_html)
    const overview_summary_html = fixThatArrayWithNullShit(plugin.overview_summary_html)
    const revenue_analysis_html = fixThatArrayWithNullShit(plugin.revenue_analysis_html)

    const revenueRange = (lower_bound != null && upper_bound != null)
        ? `${formatCurrency(lower_bound)} - ${formatCurrency(upper_bound)}`
        : "N/A";

    return (
        <Container maxWidth="md">
            <Paper elevation={3} style={{ padding: "2em", marginTop: "2em" }}>
                <Typography variant="h4" gutterBottom>
                    {plugin.name} ({plugin.marketplace_name})
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mt={2}>
                    <Typography variant="body1">
                        {plugin.user_count ? `${formatNumber(plugin.user_count)} Users` : "N/A"}
                    </Typography>
                    <Rating
                        name="plugin-avg-rating"
                        value={plugin.avg_rating ? plugin.avg_rating : 0}
                        precision={0.25}
                        readOnly
                    />
                    <Typography variant="body2">
                        {plugin.rating_count ? `${plugin.rating_count.toLocaleString()} Ratings` : "N/A"}
                    </Typography>
                </Box>
                <List>
                    <ListItem>
                        <ListItemText
                            primary="Marketplace ID"
                            secondary={plugin.marketplace_id || "N/A"}
                        />
                        <ListItemText
                            primary={`See on ${plugin.marketplace_name} Marketplace`}
                            secondary={
                                <ExternalLink
                                    href={plugin.marketplace_link || "#"}
                                >
                                    Link
                                </ExternalLink>
                            }
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Revenue Estimate" secondary={revenueRange} />
                        <ListItemText
                            primary="Pricing Tiers"
                            secondary={<ListBoxOneLine listOfStrings={plugin.pricing_tiers} />}
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Main Integrations"
                            secondary={<ListBoxOneLine listOfStrings={plugin.main_integrations} />}
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Tags"
                            secondary={<ListBoxOneLine listOfStrings={plugin.tags} />}
                        />
                    </ListItem>
                </List>

                {/* Timeseries Chart */}
                <Box mt={4}>
                    <Typography variant="h5">Historical Downloads & Ratings</Typography>
                    <PluginTimeseriesChart data={timeseriesData} />
                </Box>

                {/* Blog-style Content */}

                {plugin.elevator_pitch ? (
                    <Box mt={4}>
                        <Typography variant="h5">Elevator Pitch</Typography>
                        <Typography paragraph>{plugin.elevator_pitch}</Typography>
                    </Box>
                ) : null}
                {reviews_summary_html ? (
                    <BoxWithInnerHtml heading="Customers Say" htmlContent={reviews_summary_html} />
                ) : null}
                {overview_summary_html ? (
                    <BoxWithInnerHtml heading="Overview Summary" htmlContent={overview_summary_html} />
                ) : null}
                {revenue_analysis_html ? (
                    <BoxWithInnerHtml heading="Revenue Analysis" htmlContent={revenue_analysis_html} />
                ):null}
            </Paper>
        </Container>
    );
}
