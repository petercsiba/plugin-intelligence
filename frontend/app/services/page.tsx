"use client"
import React, {useState} from 'react';
import {
    Alert,
    Box,
    Button,
    Card,
    CardActions,
    CardContent,
    Container,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    Grid,
    Select,
    Snackbar,
    TextField,
    Typography
} from '@mui/material';
import PageTitle from "@/components/PageTitle";
import ExternalLink from "@/components/ExternalLink";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

const ServicesPage = () => {
    const [action, setAction] = useState('download_report');

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        job_position: '',
        intent: '',
        message: '',
        action: action,
    });

    const [dialogOpen, setDialogOpen] = useState(false);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');
    const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

    const handleClickOpen = (action: string) => {
        setDialogOpen(true);
        setAction(action);
        formData.action = action;
    };

    const handleClose = () => {
        setDialogOpen(false);
    };

    const handleChange = (e: any) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSnackbarClose = () => {
        setSnackbarOpen(false);
    };


    const [isMessageFocused, setIsMessageFocused] = useState(false);
    const handleFocus = () => setIsMessageFocused(true);
    const handleBlur = () => {
        if (!formData.message) {
            setIsMessageFocused(false);
        }
    };

    const handleSubmit = async () => {
        // Verify email is correct
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(formData.email)) {
            setSnackbarMessage("Please enter a valid email address.");
            setSnackbarSeverity('error');
            setSnackbarOpen(true);
            return;
        }

        // Handle form submission logic
        try {
            const response = await fetch(`${baseUrl}/submit_form`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                setDialogOpen(false);
                const message = action === 'download_report' ? 'Thank you! We got your message. Your download will start shortly.' : 'Thank you! We got your message.';
                setSnackbarMessage(message);
                setSnackbarSeverity('success');

                if (action === 'download_report') {
                    // Wait for 2 seconds before triggering the download
                    setTimeout(() => {
                        // Trigger file download
                        const fileUrl = '/reports/plugin-intelligence-report-2024-q2.pdf';
                        const link = document.createElement('a');
                        link.href = fileUrl;
                        link.setAttribute('download', 'plugin-intelligence-report-2024-q2.pdf');
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }, 1500); // 1500 milliseconds = 1.5 seconds
                }
            } else {
                setSnackbarMessage("Oh this is embarrassing, contact us directly at peter@plugin-intelligence.com.");
                setSnackbarSeverity('error');
            }
        } catch (error) {
            setSnackbarMessage("Oh this is embarrassing, contact us directly at peter@plugin-intelligence.com.");
            setSnackbarSeverity('error');
        }

        setSnackbarOpen(true);
    };

    return (
        <Container maxWidth="lg">
            <PageTitle title={"Services Offered"} />
            <Grid container spacing={4}>
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Box mx={2}>
                                <Typography variant="h5" component="div">
                                    For Curious Minds
                                </Typography>
                                <Typography variant="body1" color="textSecondary">
                                    <ul>
                                        <li>10 surprising insights on Plugin Marketplaces</li>
                                        <li>5 handpicked developers for your deal flow</li>
                                        <li>16 charts</li>
                                    </ul>
                                </Typography>
                            </Box>
                        </CardContent>
                        <CardActions>
                            <Box display="flex" justifyContent="center" width="100%" mb={2}>
                                <Button variant="contained" color="primary" onClick={() => handleClickOpen('download_report')}>
                                    Download the Free Report
                                </Button>
                            </Box>
                        </CardActions>
                    </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h5" component="div">
                                For Data DIYers
                            </Typography>
                            <Typography variant="body1" color="textSecondary">
                                I will run my own analysis.
                            </Typography>
                            <Typography variant="body1" color="textSecondary" mt={2}>
                                <strong>Dataset includes</strong>
                                <ul>
                                    <li>5,000+ Google Workspace Addons</li>
                                    <li>100,000+ Chrome Extensions</li>
                                    <li>Raw Timeseries Data backdated til 2020</li>
                                    <li>Aggregated Developer Data</li>
                                    <li>Cleaned, Categorized and Summarized</li>
                                </ul>
                            </Typography>
                            <Typography>
                                <ExternalLink href={"https://www.datarade.ai"}>
                                    {/*<Button variant="contained" color="primary" href="https://www.datarade.ai">*/}
                                        Connect with my Data Warehouse
                                    {/*</Button>*/}
                                </ExternalLink>
                                <br />
                                <Box
                                    component="img"
                                    src="/icons/microsoft-excel-logo.svg"
                                    alt="Microsoft Excel Logo"
                                    sx={{ ml: 0.5, width: 16, height: 16 }}
                                />
                                <Box
                                    component="img"
                                    src="/icons/snowflake-logo.svg"
                                    alt="Snowflake Logo"
                                    sx={{ ml: 0.5, height: 16 }}
                                />
                                <Box
                                    component="img"
                                    src="/icons/sigma-logo.jpg"
                                    alt="Sigma Logo"
                                    sx={{ ml: 0.5, width: 16, height: 16 }}
                                />
                            </Typography>
                        </CardContent>
                        <CardActions>
                            <Box display="flex" justifyContent="center" width="100%" mb={2}>
                                <ExternalLink href={"https://www.datarade.ai"}>
                                    <Button variant="contained" color="primary">
                                        Get the Full Dataset
                                    </Button>
                                </ExternalLink>
                            </Box>
                        </CardActions>
                    </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h5" component="div">
                                White Glove Service
                            </Typography>
                            <Typography variant="body1" color="textSecondary">
                                <ul>
                                    <li>Custom Reports</li>
                                    <li>Enrich data</li>
                                    <li>Web Scraping</li>
                                    <li>Customized reports</li>
                                </ul>
                            </Typography>
                        </CardContent>
                        <CardActions>
                            <Box display="flex" justifyContent="center" width="100%" mb={2}>
                                <Button variant="contained" color="primary" onClick={() => handleClickOpen('lets_talk')}>
                                    Lets Talk
                                </Button>
                            </Box>
                        </CardActions>
                    </Card>
                </Grid>
            </Grid>
            <Dialog open={dialogOpen} onClose={handleClose}>
                <DialogTitle>Let us better understand you to provide you with the best insights</DialogTitle>
                <DialogContent>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                autoFocus
                                margin="dense"
                                name="name"
                                label="Name"
                                type="text"
                                variant="outlined"
                                fullWidth
                                value={formData.name}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                margin="dense"
                                name="email"
                                label="Email"
                                type="email"
                                variant="outlined"
                                fullWidth
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                margin="dense"
                                name="jobPosition"
                                label="Job Position"
                                type="text"
                                variant="outlined"
                                fullWidth
                                value={formData.job_position}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth margin="dense">
                                {/*<InputLabel id="intent-label">Intent</InputLabel>*/}
                                <Select
                                    labelId="intent-label"
                                    id="intent"
                                    name="intent"
                                    value={formData.intent}
                                    onChange={handleChange}
                                    native
                                >
                                    <option value="default">Select Use Case ...</option>
                                    <option value="analysis">Marketing</option>
                                    <option value="enrich-data">Investment Scouting</option>
                                    <option value="scraping">Competitor Analysis</option>
                                    <option value="reports">For a Blogpost</option>
                                    <option value="just-curious">Just Curious</option>
                                    <option value="other">Other</option>
                                </Select>
                            </FormControl>
                        </Grid>
                        {action === 'lets_talk' && (
                            <Grid item xs={12}>
                                <TextField
                                    margin="dense"
                                    name="message"
                                    label="Message"
                                    type="text"
                                    variant="outlined"
                                    fullWidth
                                    multiline
                                    rows={4}
                                    value={isMessageFocused ? formData.message : 'Hi Peter,\nLove the site,\nI would like to ...'}
                                    onChange={handleChange}
                                    onFocus={handleFocus}
                                    onBlur={handleBlur}
                                    InputProps={{
                                        style: {
                                            color: isMessageFocused || formData.message ? 'inherit' : 'gray',
                                        },
                                    }}
                                />
                            </Grid>
                        )}
                    </Grid>
                </DialogContent>

                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button variant="contained" onClick={handleSubmit} color="primary">
                        {action === 'download_report' ? 'Download Report' : 'Submit Inquiry'}
                    </Button>
                </DialogActions>
            </Dialog>
            <Snackbar
                open={snackbarOpen}
                autoHideDuration={5000}
                onClose={handleSnackbarClose}
                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
                <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
                    {snackbarMessage}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default ServicesPage;
