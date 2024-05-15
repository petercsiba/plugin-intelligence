import React from 'react';
import { Box, Typography, Divider } from '@mui/material';

interface ListBoxOneLineProps {
    listOfStrings: string[] | undefined;
}

const ListBoxOneLine: React.FC<ListBoxOneLineProps> = ({ listOfStrings }) => {
    return (
        <Box display="flex" alignItems="center" flexWrap="wrap">
            {listOfStrings?.map((value, index, array) => (
                <React.Fragment key={index}>
                    <Typography variant="body2">{value}</Typography>
                    {index < array.length - 1 && <Divider orientation="vertical" flexItem style={{ margin: '0 8px' }} />}
                </React.Fragment>
            )) || <Typography variant="body2">Unknown</Typography>}
        </Box>
    );
};

export default ListBoxOneLine;
