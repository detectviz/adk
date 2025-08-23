# Example Incident State Document

Shakespeare Sonnet++ Overload: 2015-10-21 Incident management info: https://incident-management-cheat-sheet

(Communications lead to keep summary updated.) Summary : Shakespeare search service in cascading failure due to newly discovered sonnet not in search index.

Status : active, incident #465

Command Post(s) : #shakespeare on IRC



Command Hierarchy (all responders)

Current Incident Commander: jennifer Operations lead: docbrown Planning lead: jennifer Communications lead: jennifer Next Incident Commander: to be determined

- Current Incident Commander: jennifer Operations lead: docbrown Planning lead: jennifer Communications lead: jennifer

Current Incident Commander: jennifer

Operations lead: docbrown Planning lead: jennifer Communications lead: jennifer

- Operations lead: docbrown

- Planning lead: jennifer

- Communications lead: jennifer

- Next Incident Commander: to be determined

Next Incident Commander: to be determined

(Update at least every four hours and at handoff of Comms Lead role.) Detailed Status (last updated at 2015-10-21 15:28 UTC by jennifer)

Exit Criteria:

New sonnet added to Shakespeare search corpus TODO Within availability (99.99%) and latency (99%ile < 100 ms) SLOs for 30+ minutes TODO

- New sonnet added to Shakespeare search corpus TODO

- Within availability (99.99%) and latency (99%ile < 100 ms) SLOs for 30+ minutes TODO

TODO list and bugs filed:

Run MapReduce job to reindex Shakespeare corpus DONE Borrow emergency resources to bring up extra capacity DONE Enable flux capacitor to balance load between clusters (Bug 5554823) TODO

- Run MapReduce job to reindex Shakespeare corpus DONE

- Borrow emergency resources to bring up extra capacity DONE

- Enable flux capacitor to balance load between clusters (Bug 5554823) TODO

Incident timeline (most recent first: times are in UTC)

2015-10-21 15:28 UTC jennifer Increasing serving capacity globally by 2x 2015-10-21 15:21 UTC jennifer Directing all traffic to USA-2 sacrificial cluster and draining traffic from other clusters so they can recover from cascading failure while spinning up more tasks MapReduce index job complete, awaiting Bigtable replication to all clusters 2015-10-21 15:10 UTC martym Adding new sonnet to Shakespeare corpus and starting index MapReduce 2015-10-21 15:04 UTC martym Obtains text of newly discovered sonnet from shakespeare-discuss@ mailing list 2015-10-21 15:01 UTC docbrown Incident declared due to cascading failure 2015-10-21 14:55 UTC docbrown Pager storm, ManyHttp500s in all clusters

- 2015-10-21 15:28 UTC jennifer Increasing serving capacity globally by 2x

2015-10-21 15:28 UTC jennifer

Increasing serving capacity globally by 2x

- Increasing serving capacity globally by 2x

- 2015-10-21 15:21 UTC jennifer Directing all traffic to USA-2 sacrificial cluster and draining traffic from other clusters so they can recover from cascading failure while spinning up more tasks MapReduce index job complete, awaiting Bigtable replication to all clusters

2015-10-21 15:21 UTC jennifer

Directing all traffic to USA-2 sacrificial cluster and draining traffic from other clusters so they can recover from cascading failure while spinning up more tasks MapReduce index job complete, awaiting Bigtable replication to all clusters

- Directing all traffic to USA-2 sacrificial cluster and draining traffic from other clusters so they can recover from cascading failure while spinning up more tasks

- MapReduce index job complete, awaiting Bigtable replication to all clusters

- 2015-10-21 15:10 UTC martym Adding new sonnet to Shakespeare corpus and starting index MapReduce

2015-10-21 15:10 UTC martym

Adding new sonnet to Shakespeare corpus and starting index MapReduce

- Adding new sonnet to Shakespeare corpus and starting index MapReduce

- 2015-10-21 15:04 UTC martym Obtains text of newly discovered sonnet from shakespeare-discuss@ mailing list

2015-10-21 15:04 UTC martym

Obtains text of newly discovered sonnet from shakespeare-discuss@ mailing list

- Obtains text of newly discovered sonnet from shakespeare-discuss@ mailing list

- 2015-10-21 15:01 UTC docbrown Incident declared due to cascading failure

2015-10-21 15:01 UTC docbrown

Incident declared due to cascading failure

- Incident declared due to cascading failure

- 2015-10-21 14:55 UTC docbrown Pager storm, ManyHttp500s in all clusters

2015-10-21 14:55 UTC docbrown

Pager storm, ManyHttp500s in all clusters

- Pager storm, ManyHttp500s in all clusters

