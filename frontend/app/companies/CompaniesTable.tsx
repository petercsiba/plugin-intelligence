import {formatNumber, formatNumberShort} from "@/utils";

import NextLink from "next/link";
import Button from '@mui/material/Button';
import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import {CompaniesTopResponse} from "./models";


interface CompaniesTableProps {
  companies: CompaniesTopResponse[];
}

const CompaniesTable: React.FC<CompaniesTableProps> = ({ companies }) => {
    return (
        <TableContainer component={Paper}>
            <Table size="small"> {/* Smaller cell padding */}
                <TableHead>
                    <TableRow>
                        <TableCell>Logo</TableCell>
                        <TableCell style={{
                            maxWidth: '150px',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis'
                        }}>Name</TableCell>
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
                                    <img src={company.img_logo_link} alt={company.display_name} style={{width: 48}}/>
                                ) : (
                                    ''
                                )}
                            </TableCell>
                            <TableCell style={{
                                fontWeight: "bold",
                                maxWidth: '150px',
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis'
                            }}>{company.display_name}</TableCell>
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
    )
}
export default CompaniesTable;