# Eliminating Toil

Written by Vivek Rau Edited by Betsy Beyer

If a human operator needs to touch your system during normal operations, you have a bug. The definition of normal changes as your systems grow. Carla Geisser, Google SRE

If a human operator needs to touch your system during normal operations, you have a bug. The definition of normal changes as your systems grow.

Carla Geisser, Google SRE

In SRE, we want to spend time on long-term engineering project work instead of operational work. Because the term operational work may be misinterpreted, we use a specific word: toil .

## Toil Defined

Toil is not just "work I donât like to do." Itâs also not simply equivalent to administrative chores or grungy work. Preferences as to what types of work are satisfying and enjoyable vary from person to person, and some people even enjoy manual, repetitive work. There are also administrative chores that have to get done, but should not be categorized as toil: this is overhead . Overhead is often work not directly tied to running a production service, and includes tasks like team meetings, setting and grading goals, 19 snippets, 20 and HR paperwork. Grungy work can sometimes have long-term value, and in that case, itâs not toil, either. Cleaning up the entire alerting configuration for your service and removing clutter may be grungy, but itâs not toil.

So what is toil? Toil is the kind of work tied to running a production service that tends to be manual, repetitive, automatable, tactical, devoid of enduring value, and that scales linearly as a service grows. Not every task deemed toil has all these attributes, but the more closely work matches one or more of the following descriptions, the more likely it is to be toil:

# Why Less Toil Is Better

Our SRE organization has an advertised goal of keeping operational work (i.e., toil) below 50% of each SREâs time. At least 50% of each SREâs time should be spent on engineering project work that will either reduce future toil or add service features. Feature development typically focuses on improving reliability, performance, or utilization, which often reduces toil as a second-order effect.

We share this 50% goal because toil tends to expand if left unchecked and can quickly fill 100% of everyoneâs time. The work of reducing toil and scaling up services is the "Engineering" in Site Reliability Engineering. Engineering work is what enables the SRE organization to scale up sublinearly with service size and to manage services more efficiently than either a pure Dev team or a pure Ops team.

Furthermore, when we hire new SREs, we promise them that SRE is not a typical Ops organization, quoting the 50% rule just mentioned. We need to keep that promise by not allowing the SRE organization or any subteam within it to devolve into an Ops team.

If we seek to cap the time an SRE spends on toil to 50%, how is that time spent?

Thereâs a floor on the amount of toil any SRE has to handle if they are on-call. A typical SRE has one week of primary on-call and one week of secondary on-call in each cycle (for discussion of primary versus secondary on-call shifts, see Being On-Call ). It follows that in a 6-person rotation, at least 2 of every 6 weeks are dedicated to on-call shifts and interrupt handling , which means the lower bound on potential toil is 2/6 = 33% of an SREâs time. In an 8-person rotation, the lower bound is 2/8 = 25%.

Consistent with this data, SREs report that their top source of toil is interrupts (that is, non-urgent service-related messages and emails). The next leading source is on-call (urgent) response, followed by releases and pushes. Even though our release and push processes are usually handled with a fair amount of automation, thereâs still plenty of room for improvement in this area.

Quarterly surveys of Googleâs SREs show that the average time spent toiling is about 33%, so we do much better than our overall target of 50%. However, the average doesnât capture outliers: some SREs claim 0% toil (pure development projects with no on-call work) and others claim 80% toil. When individual SREs report excessive toil, it often indicates a need for managers to spread the toil load more evenly across the team and to encourage those SREs to find satisfying engineering projects.

# What Qualifies as Engineering?

Engineering work is novel and intrinsically requires human judgment. It produces a permanent improvement in your service, and is guided by a strategy. It is frequently creative and innovative, taking a design-driven approach to solving a problem the more generalized, the better. Engineering work helps your team or the SRE organization handle a larger service, or more services, with the same level of staffing.

Typical SRE activities fall into the following approximate categories:

Every SRE needs to spend at least 50% of their time on engineering work, when averaged over a few quarters or a year. Toil tends to be spiky, so a steady 50% of time spent on engineering may not be realistic for some SRE teams, and they may dip below that target in some quarters. But if the fraction of time spent on projects averages significantly below 50% over the long haul, the affected team needs to step back and figure out whatâs wrong.

# Is Toil Always Bad?

Toil doesnât make everyone unhappy all the time, especially in small amounts. Predictable and repetitive tasks can be quite calming. They produce a sense of accomplishment and quick wins. They can be low-risk and low-stress activities. Some people gravitate toward tasks involving toil and may even enjoy that type of work.

Toil isnât always and invariably bad, and everyone needs to be absolutely clear that some amount of toil is unavoidable in the SRE role, and indeed in almost any engineering role. Itâs fine in small doses, and if youâre happy with those small doses, toil is not a problem. Toil becomes toxic when experienced in large quantities. If youâre burdened with too much toil, you should be very concerned and complain loudly. Among the many reasons why too much toil is bad, consider the following:

Additionally, spending too much time on toil at the expense of time spent engineering hurts an SRE organization in the following ways:

# Conclusion

If we all commit to eliminate a bit of toil each week with some good engineering, weâll steadily clean up our services, and we can shift our collective efforts to engineering for scale, architecting the next generation of services, and building cross-SRE toolchains. Letâs invent more, and toil less.

19 We use the Objectives and Key Results system, pioneered by Andy Grove at Intel; see [Kla12] .

20 Googlers record short free-form summaries, or "snippets," of what weâve worked on each week.

21 We have to be careful about saying a task is "not toil because it needs human judgment." We need to think carefully about whether the nature of the task intrinsically requires human judgment and cannot be addressed by better design. For example, one could build (and some have built) a service that alerts its SREs several times a day, where each alert requires a complex response involving plenty of human judgment. Such a service is poorly designed, with unnecessary complexity. The system needs to be simplified and rebuilt to either eliminate the underlying failure conditions or deal with these conditions automatically. Until the redesign and reimplementation are finished, and the improved service is rolled out, the work of applying human judgment to respond to each alert is definitely toil.