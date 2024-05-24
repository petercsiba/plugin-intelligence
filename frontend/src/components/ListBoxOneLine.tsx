import React from 'react';
import { Box, Typography, Divider } from '@mui/material';

interface ListBoxOneLineProps {
    listOfStrings: string[] | undefined;
}

// NOTE: This component uses Box so when used with ListItemText, you need to add
// <ListItemText secondaryTypographyProps={{ component: 'div' }}
const ListBoxOneLine: React.FC<ListBoxOneLineProps> = ({ listOfStrings }) => {
    // TODO(P2, ux): This sometimes renders as one element without the separators
    console.log("listOfStrings", listOfStrings)
    return (
        <Box display="flex" alignItems="center" flexWrap="wrap">
            {listOfStrings?.map((value, index, array) => (
                <React.Fragment key={index}>
                    <Typography variant="body2" component="span">{value}</Typography>
                    {index < array.length - 1 && <Divider orientation="vertical" flexItem style={{ margin: '0 8px' }} />}
                </React.Fragment>
            )) || <Typography variant="body2">Unknown</Typography>}
        </Box>
    );
};

export default ListBoxOneLine;
