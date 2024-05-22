import React from 'react';
import {
    Container,
    Typography,
    List,
    ListItem,
    ListItemText,
} from '@mui/material';

const TermsOfService: React.FC = () => {
    return (
        <Container maxWidth="md" sx={{ padding: '2rem 0' }}>
            <Typography variant="h3" gutterBottom>Terms of Service</Typography>
            <Typography variant="body1" gutterBottom><em>Last Updated May 22, 2024</em></Typography>

            <Typography variant="body1" paragraph>
                This Master Service Agreement (the “<strong>Agreement</strong>”) is an agreement between Plugin Intelligence ,
                (“<strong>Plugin Intelligence</strong>”), a sole proprietorship with EIN: 99-3162250, and you or the entity you represent (“<strong>Client</strong>”). This Agreement takes effect when you sign up to Plugin Intelligence or, if earlier, when you access or use the Plugin Intelligence services, as defined below (the “<strong>Effective Date</strong>”). If you are using the Plugin Intelligence services on behalf of an entity, you represent to us that you are lawfully able to enter into this Agreement on behalf of the Client.
            </Typography>

            <Typography variant="h4" id="responsibilities" gutterBottom>1. Plugin Intelligence Responsibilities</Typography>
            <List>
                <ListItem>
                    <ListItemText primary="
                    Plugin Intelligence will make any of the services detailed in this Agreement or otherwise
                    offered on the Plugin Intelligence platforms (“the Services”) available to Client
                    in accordance with the provisions of this Agreement,
                    including Plugin Intelligence’s Service Level Agreement, if applicable.
                     Plugin Intelligence shall have the right, but not the obligation,
                     to monitor Client’s use of the Service for billing purposes and to verify no misuse or network abuse.
                     Plugin Intelligence may share the Client’s relevant information with any authority in case of a complaint,
                     investigation or a lawsuit, if Plugin Intelligence determines that it is necessary to comply with any subpoena,
                     judicial or governmental requirement, or order." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Certain Services will be made available subject to Plugin Intelligence’s completion of a successful compliance review process of the Client. Such review may include a Know Your Client process, video calls with the Client and any other measures that Plugin Intelligence decides, at its sole discretion, are necessary to approve Client’s use of the Service. Client will cooperate with Plugin Intelligence and provide it with any information reasonably required as part of the compliance review process." />
                </ListItem>
            </List>

            <Typography variant="h4" id="suspension" gutterBottom>2. Temporary Suspension</Typography>
            <Typography variant="body1" paragraph>
                Plugin Intelligence in its sole discretion and at any time, may suspend Client’s right to access or use the Service immediately upon notice to Client if Plugin Intelligence, at its sole discretion, determines that:
            </Typography>
            <List>
                <ListItem>
                    <ListItemText primary="Client’s use of or registration to the Service (i) poses a security risk to Plugin Intelligence or its Service or any third party, (ii) may adversely impact Plugin Intelligence or any of its clients, including by way of causing a user to be blocked from certain websites, networks or services, (iii) may subject Plugin Intelligence, its affiliates, or any third party to liability, or is in breach under any applicable laws or regulations, (iv) may be fraudulent, or (v) may disparage or devalue Plugin Intelligence’s reputation or goodwill;" />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Client is in breach of this Agreement, including if Client is delinquent on payment obligations;" />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Client has violated any of its representations and warranties under this Agreement or any other representation and warranties provided to Plugin Intelligence associated with Client’s use of the Service." />
                </ListItem>
            </List>

            <Typography variant="h4" id="warranties" gutterBottom>3. Client Warranties and Representations</Typography>
            <Typography variant="body1" paragraph>
                The Client warrants, represents and covenants to Plugin Intelligence that:
            </Typography>
            <List>
                <ListItem>
                    <ListItemText primary="It is aware that the Services may only be used by individuals that are at least 18 years old and at least the legal age allowed for by the applicable jurisdiction. The Client represents and warrants that, to the extent it is an individual, it is of legal age, as described above. Client further acknowledges that Plugin Intelligence may require proof of age as a condition for the provision of the Service." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="To the extent that the use of the Service will contain any personal information, that is intended for processing by Plugin Intelligence as a “processor” (as the term is defined in the applicable privacy legislation) then the provision of the Service will also be subject to the Data Protection Addendum." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The Client will be solely responsible for any actions it performs based on the use of the Service." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The Client is responsible for protecting its personal username and/or password to the Service. The Client may not share its account privileges with anyone or knowingly permit any unauthorized access to the Service. The accounts of those involved will be disabled if sharing is detected." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The Client shall not use the Services in violation of applicable law or regulations or any third party rights (including intellectual property rights) and not use the Service in any manner or for any purpose other than as stated in the intended use case provided to Plugin Intelligence, if applicable." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Without derogating from the generality of the above, the Client will only use the Service in accordance with the Acceptable Use Policy, as may be amended from time to time." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="When using the Proxy Services, the Client shall not use the Service to: (i) distribute cracking, warez, ROM, virus, adware, worms, trojan horses, malware, spyware or any other similar malicious activities and products or any other computer code, files or programs designed to interrupt, hijack, destroy, limit or adversely affect the functionality of any computer software, hardware, network or telecommunications equipment; (ii) cause any network resource to be unavailable to its intended users, including, without limitation, via “Denial-of-Service (DoS)” or “Distributed Denial-of-Service (DDoS)” attack; (iii) distribute any unlawful content or encourage any unlawful activity; (iv) cause any damage or service disruption to any third party computers or service; or (v) enhance or operate a service that competes with the Services, or assist any other party to do so." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Not use other systems, products or services that infringe upon the patents and other intellectual property rights of Plugin Intelligence." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Not engage in any reselling of the Service in whole or in part, without Plugin Intelligence’s prior written authorization." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Not, and not enable others to, copy, decompile, reverse engineer, disassemble, attempt to derive the source code of, decrypt, modify, or create derivative works of the Service or any services provided by Plugin Intelligence, or any part thereof, including without limitation by using the Service in order to perform mapping of the IP addresses used by Plugin Intelligence in the provision of the Service, without Plugin Intelligence’s prior written approval. It is hereby clarified that IP addresses used as part of the provision of the Service are personal and confidential information, and any unauthorized use of such information is strictly prohibited and may be considered breach of applicable law and/or third party rights." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="When using the Data Services, the Client shall not distribute, transmit, reproduce, publish, license, transfer, or sell any Data in order to offer a similar or competitive product." />
                </ListItem>
            </List>

            <Typography variant="h4" id="consideration" gutterBottom>4. Consideration</Typography>
            <List>
                <ListItem>
                    <ListItemText primary="Following the free trial period (if granted by Plugin Intelligence), Client will enter a valid payment method as a condition for further use or access to the Service, at the consideration stated in the Client’s dashboard or in a specific insertion order or other statement of work (the “Subscription Fees”). The Subscription Fees are non-cancelable and non-refundable." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Prices are net of any withholding or other taxes and the Client shall be responsible for payment of all such applicable taxes, levies, or duties." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Client consents to receive electronic invoices and receipts from Plugin Intelligence." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="In the event of non-payment of the Subscription Fees in accordance with the terms hereof, the Client agrees to pay for the costs and expenses of collection of any unpaid deficiency in the Client’s account, including, but not limited to, attorney’s fees, court costs and any other costs incurred or paid by Plugin Intelligence." />
                </ListItem>
            </List>

            <Typography variant="h4" id="confidential-information" gutterBottom>5. Confidential Information</Typography>
            <Typography variant="body1" paragraph>
                If a Party (the “Receiving Party”) obtains access to Confidential Information (as defined below) of the other Party (the “Disclosing Party”) in connection with the negotiation of or performance under this Agreement, the Receiving Party agrees that:
            </Typography>
            <List>
                <ListItem>
                    <ListItemText primary="The Disclosing Party shall retain ownership of the Confidential Information and that the Receiving Party shall not acquire any rights therein, except the right to use such Confidential Information to the extent provided in this Agreement;" />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The Receiving Party shall use at least the same degree of care to protect the Confidential Information from unauthorized disclosure or access that the Receiving Party uses to protect its own Confidential Information, but not less than reasonable care, including measures to protect against the unauthorized use, access, destruction, loss and alteration of such Confidential Information;" />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Except as otherwise provided in this Agreement, no Confidential Information disclosed pursuant to this Agreement shall be made available by the Receiving Party to any third party for any purpose, except to a consultant, attorney, subcontractor, or potential subcontractor who needs to know the Confidential Information for the performance of this Agreement and provided that they agree to be bound by the terms and conditions of this Article or another written agreement sufficient to require them to treat Confidential Information in accordance with this Agreement. The Receiving Party agrees to indemnify the Disclosing Party for any violation or breach of such restrictions." />
                </ListItem>
            </List>
            <Typography variant="body1" paragraph>
                “Confidential Information” shall mean all information disclosed by the Disclosing Party to the Receiving Party in connection with the Agreement, whether in oral form, visual form or in writing, including but not limited to: all specifications, formulas, prototypes, computer programs and any and all records, data, ideas, methods, techniques, processes and projections, plans, marketing information, materials, creatives, scripts and storyboards, financial statements, memoranda, analyses, notes, legal documents and other data and information (in whatever form), as well as improvements, patents (whether pending or duly registered), trade secrets, any know-how, customer lists, customer information, end-user information, and any information provided to the Disclosing Party by a third party under a confidentiality agreement or which the Disclosing Party is otherwise legally obligated to keep in confidence, relating to the Disclosing Party, and information learned by the Receiving Party from the Disclosing Party through inspection of Disclosing Party’s property, that relates to the Disclosing Party’s products, designs, business plans, business opportunities, finances, research, development, know-how or personnel. The Subscription Fees under this Agreement, shall be considered as Confidential Information.
            </Typography>
            <Typography variant="body1" paragraph>
                Confidential Information will not include:
            </Typography>
            <List>
                <ListItem>
                    <ListItemText primary="Information that the Receiving Party received rightfully from a third party who has the right to transfer or disclose it, without default or breach of this Agreement;" />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Information that was previously rightfully known by the Receiving Party free of any obligation to keep it confidential;" />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Information that becomes publicly known through no wrongful act of the Receiving Party;" />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Information that is independently developed by the Receiving Party without reference to, use of, or access to the Confidential Information of the Disclosing Party." />
                </ListItem>
            </List>
            <Typography variant="body1" paragraph>
                The Receiving Party may disclose Confidential Information pursuant to a subpoena, judicial or governmental requirement, or order, and the Receiving Party shall not be liable in damages for any such disclosure of Confidential Information.
            </Typography>
            <Typography variant="body1" paragraph>
                The confidentiality obligations under this Agreement will survive any expiration or termination of this Agreement.
            </Typography>

            <Typography variant="h4" id="disclaimer-warranties" gutterBottom>6. Disclaimer of Warranties</Typography>
            <Typography variant="body1" paragraph>
                PLUGIN INTELLIGENCE IS PROVIDING THE USE OF THE SERVICE AND ANY ACCOMPANYING DATA ON “AS IS” BASIS AND IT EXPRESSLY DISCLAIMS ANY AND ALL REPRESENTATIONS AND WARRANTIES, WHETHER EXPRESS OR IMPLIED TO THE CONDITION, VALUE OR QUALITY OF THE SERVICE OR ANY ACCOMPANYING DATA, INCLUDING, WITHOUT LIMITATION, ANY WARRANTIES OF MERCHANTABILITY, SUITABILITY OR FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, SECURITY, ACCURACY, ABSENCE OF VIRUSES OR ANY DEFECT THEREIN, WARRANTIES ARISING FROM A COURSE OF DEALING, USAGE OR TRADE PRACTICE. PLUGIN INTELLIGENCE FURTHER EXPRESSLY DISCLAIMS ANY REPRESENTATIONS OR WARRANTIES THAT THE USE OF THE SERVICE WILL BE CONTINUOUS, UNINTERRUPTED OR ERROR-FREE, OR THAT ANY INFORMATION CONTAINED THEREIN WILL BE ACCURATE OR COMPLETE.
            </Typography>

            <Typography variant="h4" id="limitation-liability" gutterBottom>7. Limitation of Liability</Typography>
            <Typography variant="body1" paragraph>
                In no event will Plugin Intelligence be liable under this Agreement for any consequential, special, indirect or punitive damages or for any loss, profits or revenue (whether in contract, tort, negligence or any other legal theory) in any way relating to this Agreement (“<strong>Event</strong>”), even if Plugin Intelligence had been informed in advance of the possibility of such damages. Plugin Intelligence’s aggregated liability under this Agreement for any claim or damage or series of such is limited to the amount of fees actually received by Plugin Intelligence from Client under this Agreement during the one month period prior to the Event.
            </Typography>

            <Typography variant="h4" id="indemnification" gutterBottom>8. Indemnification</Typography>
            <Typography variant="body1" paragraph>
                Client will defend Plugin Intelligence against any claim, demand, suit or proceeding made or brought against Plugin Intelligence by a third party alleging that the Client’s use of any Service infringes or misappropriates such third party’s intellectual property rights or breaches applicable privacy laws or any other applicable law or causes damage to such third party (a “<strong>Claim Against Plugin Intelligence</strong>”), and will indemnify Plugin Intelligence from any direct damages, attorney fees and costs finally awarded against Plugin Intelligence as a result of, or for any amounts paid by Plugin Intelligence under a court-approved settlement of, a Claim Against Plugin Intelligence, provided Plugin Intelligence (a) promptly gives Client written notice of the Claim Against Plugin Intelligence, (b) gives Client sole control of the defense and settlement of the Claim Against Plugin Intelligence (except that Client may not settle any Claim against Plugin Intelligence unless it unconditionally releases Plugin Intelligence of all liability), (c) gives Client all reasonable assistance, at Client’s expense, and (d) Plugin Intelligence shall not negotiate or enter into any settlement for this matter without Client’s prior written consent. Client’s obligations above do not apply to a Claim Against Plugin Intelligence which is based only on Plugin Intelligence’s breach of this Agreement.
            </Typography>

            <Typography variant="h4" id="term-termination" gutterBottom>9. Term and Termination</Typography>
            <List>
                <ListItem>
                    <ListItemText primary="This Agreement commences on the Effective Date and shall continue until terminated in accordance with the terms of this Agreement." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Unless a separate schedule or statement of work agreed upon between the Parties has set a pre-determined period for the provision of the Services, either party shall have the right to terminate this Agreement immediately at any time by providing the other party an advance written notice until the end of that calendar month. The Agreement will terminate at the end of the calendar month at which the written notice was received, without the party incurring any liability towards the other party by virtue of such termination." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Plugin Intelligence shall be entitled to terminate this Agreement immediately for “cause” by written notice to the Client if (a) any act or omission by Client entitles Plugin Intelligence to suspend its access or use of the System or Service as described in Section 2; (b) the Client is in breach of any representation or warranty found in this Agreement or any other representation and warranties provided to Plugin Intelligence associated with Client’s use of the System or Service; (c) the Client engages in any action or activity that, in Plugin Intelligence’s sole discretion, places Plugin Intelligence at risk under any applicable laws or regulations. Plugin Intelligence shall not be liable to the Client or any third party for the termination of this Agreement." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Upon termination, any outstanding consideration amounts shall immediately become due and payable (including without limitation, for Data collected, even if not yet provided to the Client), the license granted herein shall be terminated and the Client shall immediately stop using the System or Service." />
                </ListItem>
            </List>

            <Typography variant="h4" id="specific-service-terms" gutterBottom>10. Specific Service Terms</Typography>
            <Typography variant="body1" paragraph>
                Without derogating from the <strong>generality</strong> of other provisions of the Agreement, the following terms shall apply to the specific Services the Client wishes to obtain from Plugin Intelligence:
            </Typography>
            <Typography variant="h5" id="specific-service-terms" gutterBottom>Web Scraper Service.</Typography>
            <List component="div">
                <ListItem>
                    <ListItemText primary="Plugin Intelligence has developed, owns and offers a data collector service which collects and delivers publicly available data to its users, subject to the terms in this Agreement." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Plugin Intelligence will not provide the Service or Data where such provision may, in Plugin Intelligence’s sole discretion, infringe or violate any applicable laws or regulations or any other third party rights." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Client’s use of the data collector service is subject to all applicable laws, including without limitation data protection and privacy laws. To the extent applicable to processing of personal data, Client is solely responsible for determining the lawful grounds, providing notices, respecting data subject rights and all other related obligations." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Plugin Intelligence may retain data it has collected or delivered to its Clients and may use it for its own purposes in its sole discretion." />
                </ListItem>
            </List>
            <Typography variant="h5" id="specific-service-terms" gutterBottom>Dataset Product.</Typography>
            <List component="div">
                <ListItem>
                    <ListItemText primary="Plugin Intelligence may offer, from time to time, for various fees, digital data sets of information on various categories (“Datasets”)." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The Datasets may only be used for legally valid purposes and in accordance with all applicable laws which may apply, both domestic and international, including without limitation applicable privacy and marketing communications legislation." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The Datasets may contain additional terms and conditions governing the use of such Datasets." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="For subscription purchases of Datasets, updates will be provided if and when available." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Any requests for changes in Datasets will be subject to Plugin Intelligence’s prior approval, and may incur additional charges, as will be agreed between the Client and Plugin Intelligence." />
                </ListItem>
            </List>
            <Typography variant="h5" id="specific-service-terms" gutterBottom>Data Insights / Reports.</Typography>
            <List component="div">
                <ListItem>
                    <ListItemText primary="Plugin Intelligence may offer a service that is intended to produce various data insights based on pre-determined datasets provided by Plugin Intelligence." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The provisions of this Agreement, including without limitation, the provisions concerning Disclaimer of Warranties and Limitation of Liability, will govern the offering and possible use of such insights." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The insights do not constitute legal, financial, commercial, or other advice and any reliance on such insights is done solely in the Client’s discretion and its own risk." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="The information contained in the Plugin Intelligence Insights may not be shared with third parties without Plugin Intelligence’s prior written approval." />
                </ListItem>
            </List>

            <Typography variant="h4" id="miscellaneous" gutterBottom>11. Miscellaneous</Typography>
            <List>
                <ListItem>
                    <ListItemText primary="This Agreement constitutes the entire understanding between the parties with respect to the matters referred to herein." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="All notices or other communications hereunder shall be given by email to the email address provided by the parties as part of the registration to the Service." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="To the extent not prohibited by applicable law, the Customer waives the right to litigate in court or an arbitration proceeding any dispute related to this Agreement as a class action, either as a member of a class or as a representative." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="This Agreement shall be governed by the laws of the State of California, excluding its conflict of law rules, and the courts of San Francisco shall have exclusive jurisdiction over the parties." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="If any provision of this Agreement will be held by a court of competent jurisdiction to be contrary to any law, the remaining provisions will remain in full force and effect as if said provision never existed." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="No failure or delay on the part of any party hereto in exercising any right, power or remedy hereunder shall operate as a waiver thereof." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Plugin Intelligence may, at any time, and at its sole discretion, modify this Agreement, with or without notice to the Client. Any such modification will be effective immediately upon public posting. Client’s continued use of the Systems and Service following any such modification constitutes acceptance of the modified Agreement." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Plugin Intelligence may use Client’s name and/or logo in promotional materials and on Plugin Intelligence’s website." />
                </ListItem>
            </List>
        </Container>
    );
};

export default TermsOfService;
