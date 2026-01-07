# Custom Records Closeout with Ethan

**Date:** 2025-12-19
**Segments:** 367

---

## Transcript

**Me:** All right.

**Me:** Also the reason why this is good.

**Me:** Is because there's a mic here.

**Me:** And a mic here.

**Me:** Interesting.

**Me:** Here we go.

**Me:** Oh, I have a fixture now, by the way.

**Me:** Let me see if it works.

**Me:** I don't really know.

**Me:** How.

**Me:** Fucking.

**Me:** How fixtures work.

**Me:** Whatever.

**Me:** Starting big picture.

**Me:** Yeah.

**Me:** Dig.

**Me:** In.

**Me:** All right.

**Me:** So big picture goal right now.

**Me:** We want to get to a point where any business that is on plus.

**Me:** Can use custom records for their users so that policy agent is better.

**Me:** As part of that and along the way.

**Me:** How does Policy Agency use customer records right now? No, it was all the custom records about a user. Got it. And so you can say this user is a company phone, job title is designer or whatever.

**Me:** So huge context advantage for that. And then you get all the fun deterministic things. You've seen my policy editor thing.

**Me:** Which I think will be great, but also, yeah.

**Me:** But first things first. Let's get the ui.

**Me:** Ready to go.

**Me:** So we already see the extra columns here. This is live and prod.

**Me:** When we click. What's up? I haven't seen that. I haven't seen Live in Prod. Oh, yeah, no, it's Live on Prod. Wow. Feature flag gated. No, if you've got a custom field that shows up automatically.

**Me:** How are you doing? The columns are just sorted by recently used created time.

**Me:** By default. Fantastic. So they show up here, you can order it.

**Me:** That is massive.

**Me:** Funny how simple that is. Feels normal. Like these feel real now, which is huge.

**Me:** But we still have this custom data tab.

**Me:** And so, first things first, we're going to pull the functionality from custom data out of custom data.

**Me:** So that ideally, my vision is when we turn this on for everyone, the custom data tab is not showing, but they get all the functionality that it gives you.

**Me:** So for the customers that are already on it, fine, sure, whatever.

**Me:** For new customers. You can start using custom records without knowing that's what you're doing. It's just a custom user field.

**Me:** When we click on a user, we see shit about them. Great.

**Me:** I am working right now on when you edit the profile.

**Me:** You've got a section and you can change from software engineer to CEO.

**Me:** Or whatever it is those drop down, you do the stuff on personal.

**Me:** You did. Sorry. You weren't in the edit, though.

**Me:** Is that always there? Oh, yes.

**Me:** That was there. Always been there. Yeah.

**Me:** Got it. Okay. This was here before. It's confusing because there's, like, a different thing that's also called custom fields that come from Hris and they're garbage. Not important.

**Me:** But we had that before.

**Me:** So then we got edit profile company. We go down here.

**Me:** And we see all of our custom fields and we can edit them.

**Me:** Great. We can say this person's a CEO.

**Me:** He's actually level 10.

**Me:** We save our changes. He's also IP prod. This is not live in product.

**Me:** This is what I was talking with Alex, the identity frontend engineer about. But we change it, updates, blah, blah, blah. Good stuff.

**Me:** As part of that. What I'm trying to do on the back end or on the front end right now is like, code is basically what I want.

**Me:** Is that this is what you need to embed custom records.

**Me:** And I want it to be sort of as simple as possible. You've got Hey.

**Me:** The team is responsible for the permission checks themselves.

**Me:** Duh.

**Me:** The team is responsible for telling custom records what columns they care about and what cells are currently there.

**Me:** Everything else is custom records job to deal with, and I have to figure out how to get, like, nice callbacks and stuff to. To sort of play nicely and feel good here.

**Me:** But the big picture is great. You should be able to edit this stuff here.

**Me:** Now, in terms of what you can do in custom data that you can't do over here.

**Me:** That we need to add in. Sort of obvious, first thing, adding the fields. If you're doing yes, no, or plain text or number, that's super simple.

**Me:** Yep. If you're doing category, we've got maybe a CSV upload, whatever. But then we also. So that sort of is what you've got. And we're going to pull out that part. The other stuff you've been working on, new branch on top of master, checking that stuff in, boom. Cool. Yeah. And that'll be. That'll be in the three dot menu or wherever it is. I was even thinking, and I'm curious your thoughts on this.

**Me:** If you could figure out how to. How to add another one to the toolbar here. Oh, yeah, I can do that. That should be pretty easy. Is toolbar. Maybe it opens up like a little submodal. We don't even need a drawer. Hate drawers.

**Me:** Complicated when you have, like, a bunch of stuff now. Yeah. Yeah, maybe. Maybe we need a. Maybe it kind of makes sense for the drawer. For, like, drawers are great for creating. Yes, I think that's true. And I think drawers. I'm generally with, like, drawers kind of suck, but, like, I think there are good places. For them when you want it to be like, non intrusive with the rest of this. But I think it's a crutch in a lot of cases. Yeah, drawers and feature flags are crutches. People love feature flagging shit. And I'm like, are you not confident in your code? Just ship. The thing. I know it makes you think you shipped. Yeah, but then people are like, oh, we didn't ship that feature flag because the person responsible for owning the rollout left. And it's like, well, you didn't do your. You didn't finish then.

**Me:** Joseph not finished. I agree. Job's not finished. Job's not finished till it's in front. Have you seen biggest Kobe? I use that Kobe meme. All the Kobe meme is so good. Have you seen this, Doc? I wrote this. How to ship faster.

**Me:** Yeah.

**Me:** Got you right now. Let's do it. What is this? Amen.

**Me:** Job finish, biggest ones in my mind.

**Me:** 7, 8, 9, 10.

**Me:** Super important, especially this one.

**Me:** But this one's a big deal. This one's a big deal to me.

**Me:** Hate feature flex.

**Me:** Anyway.

**Me:** That said, we're featured, flagging this stuff as we roll it out. We don't need to feature. I think we do. Because if you create the, we can, I think. So here's the deal in terms of back end context.

**Me:** Is right now.

**Me:** There is. I'm gonna do a little shitty diagram.

**Me:** So we have core.

**Me:** Which is the name of both our code base and our main DB cluster.

**Me:** Ok. We separately have a DB cluster for custom recs.

**Me:** This is called multi db. It is the biggest pain in the ass.

**Me:** But everything lives in a separate cluster. This means we don't get joins, ever. So you can't sort if you have, like a reference to a user. You can't sort by first name because you can't join between custom X and core.

**Me:** Super painful. Yeah. Why? Bad decision. It is the world we live in.

**Me:** As part of that, we have this new. So as part of that, if you're running code, everything has access to core.

**Me:** Customrex does not have the same amount of resourcing as like the main core model of DB does.

**Me:** And so I have right now in a whole bunch of the workflows, code that evaluates our if conditions and all the other stuff.

**Me:** We augment how the workflow config works to include custom record stuff.

**Me:** Basically at runtime.

**Me:** And there's, like, this injection logic that does that.

**Me:** And it works. But if we had every single business always hit the custom rexdb previously, it would have fallen over.

**Me:** And so it's all sort of behind this feature, Flag.

**Me:** And so in the new year, part of what I'm doing and sort of my P0 is get rid of all that shit.

**Me:** Get it to a point where we can just always hit custom recs.

**Me:** Until that point. If people are creating this stuff, they also need to be creating this back end setting and toggling it. Which is why I want to stop having that setting exist so that it works.

**Me:** That sort of is the TLDR in terms of the core custom racks. So we can't just roll asap, but everything that we're doing is a clear improvement over the experience of current custom records customers that have it on.

**Me:** Certainly. So no new feature flags. Just the one. And then slowly pull away things that used to check the feature flag to not check it anymore.

**Me:** And we're confident that's safe, and then we're good. And that's sort of the GA cool. So that's my thought process there. And as long as we're adding stuff that makes the world better for our current customers, using custom records, great. No harm, no value.

**Me:** Great.

**Me:** So that's the deal there.

**Me:** But we've got sort of a couple pieces. We've got add new field, blah, blah, blah, and then we've got our actual custom objects.

**Me:** So we've got job titles. Here's our job titles. This is sort of our corresponding job title. Four column. It's like a derived field is what I've called it.

**Me:** But really the other thing that we don't have is we don't have a way to add a new job title.

**Me:** And we don't have a way to delete the current ones. And so today, the way that you would do that.

**Me:** Is we actually expose in this? Remember, this is an admin only pane.

**Me:** We do have a create here.

**Me:** It's funny if this basically search for the field to create it. Yeah. Which is like. It's not great. Like it works. Right. But ideally, in my mind, the sort of. I'm surprised there isn't just a button.

**Me:** To, like, add a new one or something? Well, my thought process had been that it should really live on this job titles page. But this job titles page isn't one that, like, makes a ton of sense unless you have the job title four. And people got really confused by all of that. And so I sort of was like we're just gonna hide that and sort of show less complexity. But I think if we have this stuff in, this part feels native. It is so much more obvious what is going on that it's not as big of a deal. So really, in my mind, we have the add new field stuff that you've already done.

**Me:** Is sort of the easiest first piece.

**Me:** And then there is the manage the options for a category.

**Me:** And that flow is where like that post endpoint, the delete endpoint to like, delete a category option. And like, really in my mind, the like. And I know this as a drawer that I'm drawing it as. But like, you can imagine it not as one is. You've got like big ramp page. You've got drawer, you've got job titles.

**Me:** And then you've got, like, maybe a little bit of information about where it's used.

**Me:** Where it's used.

**Me:** Which is really like, actually more of a what it's used by, which is like, this is used by the user. Users have job titles. Maybe job titles show up somewhere else.

**Me:** Maybe we have some version of it's used in these workflows, which we can sort of infer. But then you really just got like, the main piece of this is like, job title.

**Me:** One.

**Me:** Job title two.

**Me:** Trashcan icon to delete it.

**Me:** And then a big, like, plus new.

**Me:** But I think we need something like this.

**Me:** And that to me is like sort of a big obvious. If you create a category, we gotta drop you here. And then in addition to the like add singleton, there's probably like an upload of CSV or paste a comma separated list or whatever it is that gives you the whole thing, and you click create. And we post a list of all those strings, and then they exist, and then the pagination list works.

**Me:** But, like on this, you've also got probably a next arrow.

**Me:** Proven ones, et cetera.

**Me:** What do you think?

**Me:** So in my creation drawer that we made.

**Me:** What if my. I want to, like, update this jump there in the user. In which one? Oh, in like the user editing drawer. Yeah. You're saying. I think there's a world in which what we could do. There is. It might just be as simple as, like, if you do the type ahead stuff, we show that same create. And that's just like do the create. The endpoint should probably send you back the ID of the thing you just created, and then you can patch it. Even just like in the drawer that I made, where I can create a new customer, a custom field. Yep. Right. Yeah, that's the.

**Me:** We can talk about it.

**Me:** Things, so. That thing's so funny to me. Oh, this is old. See, we've got the icons here.

**Me:** Yeah, they removed. What was it that you buy in that? What was the thinking behind the icon? It was a bug that they showed at all.

**Me:** And I was complaining because it didn't show for Ramp Plus. And I was like, if it's stupid, if I didn't get stupid that it was there, turns out I was right.

**Me:** If we had decided it should be there, then we needed a plus icon was my thing. Okay, yeah, but you're saying, like, in this flow, I select a category when you say it's a select? Yep.

**Me:** Maybe it's a because this doesn't show for the other stuff, but maybe it is like a manage the categories as part of the flow. Or maybe it's a this create button when you do category is really more of like a next. And the next is like, tell me the stuff. And then we created all at once.

**Me:** That was part of why I was like, do you want me to include as part of the Create new field here the field options the select should start with as part of that API.

**Me:** Yeah, I'm thinking that was my thought process. There was really, like, making that a little more ergonomic for you, not a side quest.

**Me:** But just like.

**Me:** In the last two weeks, I've understood the impact and importance of this project. And also, there is no version of this. That small. But doesn't mean. Okay, so that's why we have to. Let's draw. Let's draw this. Okay. Giant piece of paper. Hell, yeah. Let's do it.

**Me:** By.

**Me:** The way. I'm graphite pill now. Yeah. It's so nice. It's so nice.

**Me:** Yeah.

**Me:** Nice, okay?

**Me:** Yeah, they just got bought by Cursor. I just thought. And I'm like, okay, Cursor is going to try to build GitHub.

**Me:** Yeah.

**Me:** Which is like, yeah.

**Me:** And like. Fair enough. They've already decided they're building Figma.

**Me:** Hey, if you got to justify that valuation somehow. Oh, yeah, yeah.

**Me:** Might as well.

**Me:** No. Yeah. I mean, what graphite's got is, like, pretty good. There's a couple. There's some front engineers who like one called JJ That, I guess, is similar. It's JJ Short for, like, Jiu Jitsu, I guess, and it does a lot of the same stuff. It is not owned by. Cursor, so maybe time to think about moving.

**Me:** But.

**Me:** I'm not right this second.

**Me:** I don't know how.

**Me:** This one.

**Me:** Plug it back in, though.

**Me:** All right.

**Me:** You're drawing.

**Me:** We're drawing.

**Me:** So I don't know if you want me drawing.

**Me:** Well.

**Me:** Fine. It's just boxes and letters, but, yeah.

**Me:** All right, so our first.

**Me:** Thing that we're going to want to start with is this.

**Me:** Yep, we're going to.

**Me:** And we're going to start doing very mini little graphite stacks here. Stack a bunch. So we're going to. I'm going to pull. Make a new branch off Master, because I'll have your thing.

**Me:** Take the code that I was kind of working on for this drawer. Just focus on the drawer.

**Me:** Yep. So.

**Me:** Which is going to be good.

**Me:** So this is our custom record drawer.

**Me:** We're still going to keep the name. We'll probably. Oh, so it's Custom Field. Yeah. How do you. Where's it? Custom Record. We call it Customer. Then there's Fields. There's a pain. So. So Custom Records is sort of what it was. So I think that in some, like, erps. They call this sort of thing a custom record is like this object that's totally sort of special. That was the name of the initial project.

**Me:** It sort of ended up turning into more of a custom fields that connect various objects, and some of the objects live in ramp.

**Me:** I have sort of just landed on if someone calls something a custom record. And I know what they're talking about, they're right. What do you think our customers should say?

**Me:** I think these are custom fields. It's called custom fields. Yep. I think they're custom fields. And the custom data is. The custom data is where, like, the fields and their values and their relationships all live together. But this is just a new custom field.

**Me:** And that sort of matches with what I call it in. In this drawer.

**Me:** Which is not to say that it's correct, but I think it does look about right for this to be called custom fields. If we separate them. I sort of like the idea of not separating them and just putting them under profile.

**Me:** Because if you added these, you care about them. I agree. But one thing at a time. Maybe we eventually do some delineation. There's like an icon that's, like, at some point, we're going to need a Ryu icon for something here, but I don't. It's fun to try to fight that. Okay, Go back. Yeah. So we've got new custom field. You give it a name. Name Makes sense. Keep name.

**Me:** Name pretty important.

**Me:** So you need name.

**Me:** Type.

**Me:** Do you think description should be under name?

**Me:** Or type reverse. I think it should. I think description should be clearly optional.

**Me:** Yeah, first of all. But I think that as such, it should be under required items. I think that required, that optional is sort of my intuition. So I think this ordering is correct.

**Me:** Does that track? Yep. Okay.

**Me:** Cool. Yeah, I never know what to put in for description.

**Me:** Yeah. I mean, description was one that Kalan thought was really important so that people wouldn't have to put all of the context about what the field means into the policy agent doc, which I think totally tracks.

**Me:** But also I think most people don't really care about it, so I'm almost like maybe that needs to be a lower additional whatever settings or something so people don't feel a need to type it in if it doesn't do anything.

**Me:** Then we have. We'll just start from the easy one. Stop on so we have string text.

**Me:** Number. It's actually a decimal, but it'll display nicely. No matter. Same deal. Yeah? Yeah. Decimal is what it's called in Python.

**Me:** That's what I'm calling my brain. We have a. Yes. No. Boolean.

**Me:** And then we've got category select.

**Me:** Yeah. So let's actually keep going with the words, because, again, this is also my learning process, because I've heard you say category and then select. Yeah. So select is what it says in here. Generally, the way that I think about it in my brain is like, first of all, we're making custom tables and then there's sort of this. This pointer to that custom table, and then you manage the rows in it.

**Me:** The playbook. I actually ended up saying very early on, like, you're categorizing your users. And I think that that has been maybe the easiest way for me to talk about this thing.

**Me:** And it. Calling it a category both implies that you're attaching it to the users and that you're using it to do bucketing.

**Me:** And they category sort of by definition has a set of items.

**Me:** That are in that category.

**Me:** So it's like, unlike the text, it is a bounded set of options, which is part of why I like calling it a category.

**Me:** Then why do you use the word select? I didn't make this pr. Where the hell did I get select from? Probably. I think Graeme's designs had select.

**Me:** Okay?

**Me:** Whatever. I think category works. Why do you're using the part of my. I wasn't using the critical thinking part of my brain when I was reading these things. No, for sure. And I mean, like, that's. Yeah, that's part of the deal. Category. But I think category is the right. Even, like, right. Here it says, like, categorize you. Which is. Which is also what it says here, to be fair, but.

**Me:** That sort of is my thought. It's like this is a category.

**Me:** I do like the, like, radio button guy here.

**Me:** What I generally had tried to do is the grid. I like the grid a lot. Part of why I liked the grid, to be fair, is that this is kind of a grid.

**Me:** But I think that, like, something that sort of communicates, like, hey, there are options here. The other thing you could do is you could do like, the rows one. Yeah. Here is like.

**Me:** Where is this, like, this guy? Kind of like that better, actually, yeah.

**Me:** Like, I kind of like rows because you'll also see, because you think about it as like a. A list of things that are rows.

**Me:** And so I think that's kind of a nice.

**Me:** Way to deal that.

**Me:** Now. Yeah. Okay. So back to our drawer. Yep. So you say that it's rows. You may be put in a description. If you are choosing to do a select, maybe we have you immediately tell us. Sorry. Yes. If you're doing, if you're doing a category, you've got to tell us what the actual, like, items for that category are. Pin that for a second. Okay. For text number and yes, no.

**Me:** If I go through this phone, and for all those, I just hit the create button. We don't need to upload anything. We don't need anything else? Nope.

**Me:** And as soon as we've done that, we should be able to do an optimistic update.

**Me:** That shows so that this table re renders with the extra columns.

**Me:** And that should just work.

**Me:** Nothing.

**Me:** And I've generally called those in a lot of places in code.

**Me:** For the number, the text and the Boolean primitives.

**Me:** Because they're not a reference. It's normally either something is like a primitive or it is a reference to either a ramp object or a.

**Me:** Category.

**Me:** Same page.

**Me:** Cool.

**Me:** Okay, now let's get into category.

**Me:** Because this is where this is with power.

**Me:** This is also and part of what needs to be figured out and I haven't figured out a perfect way to do this is every so often someone makes a text field and is like, why can't I use it?

**Me:** For the conditions in my workflow.

**Me:** Because they don't understand they need to make a category.

**Me:** Yep. Because the distinction is not immediately obvious to people.

**Me:** Maybe the answer is, in part, just like, hiding text and making it harder to make text. Like, that's literally, like, what my thought process was.

**Me:** Behind doing this, where I was like, here are the two things I think you actually want to do.

**Me:** Here are the other options.

**Me:** So they. Oh. Cause they're thinking my job titles are just text. Yeah, they're like, my job titles are text. And it's like. They are. But, like, we're not doing regex here. We're not doing. Yeah, we're not doing any of that. We could. We could be like, I. Want to convert text to. Yeah, yeah. And I could imagine a world in which there's a button that says, convert this text column to a category. Yeah, yeah.

**Me:** Yeah, it's kind of hard to do from a backend standpoint, and so I have avoided it.

**Me:** For a lot of reasons about how the data structures were designed is it was meant to be very hard to mess that kind. It was meant to be very hard to get the wrong types into the database at all.

**Me:** And as part of that, it's sort of hard to do, like a migration of changing the type of a column. Yes. It's like a total of lastern. Yeah. Could be a disaster. Yeah. It would require more effort than I have decided is currently worth it. As opposed to telling people you're holding the tool Wrong. How many people do you make? Anyone, though?

**Me:** FTE has done it a couple times. People have done a couple. Most of the time they're getting such close white glove support that it's a as long as I've enabled solutions properly, cool solutions might do it wrong and be like it's not showing correctly in the workflow. And then I'M like you're holding it wrong. Do a category, do you think? And then it's fine. Go back to the second.

**Me:** Yep.

**Me:** Do you think? Maybe. Cause now these are considerably more important.

**Me:** The ones that aren't text. Yeah, yeah, agree. And I'm thinking maybe this box is, like, you choose one of the options, you click, and underneath, there's, like, a bit more. A bit more color. Like a little closer to this. Yeah, exactly. Yeah. Literally this and just really. But plain text at the bottom categories. Use this if you want to refer to these exactly.

**Me:** Yep. Okay.

**Me:** Yeah. I think being guiding on this part is important. Exactly. Because. And it's not that customers will not understand the gravity of the fact that they are running a fake Postgres migration 100%, but that's what they're doing. And so it's. It's like, once again,

**Me:** Our customers don't know that they're being database architects. Yeah, yeah.

**Me:** We need to do everything in our power to not let them know that that's what they're doing. Let me just really quickly see how notion does this. Like, what are they? What does Noshu call it? Yeah, notion databases is what I think you're thinking of that.

**Me:** Technical.

**Me:** I guess.

**Me:** Yeah. And like notion, I think, to be fair, I think part of my notion calls them databases, is that ICP of notion loves feeling technical.

**Me:** The people who use Notion all, they love feeling technical. Well, they call it a. Maybe we could use a relation. You could call like the references or relation. And that's maybe the right way to talk about like a reference to, like an accounting field option or like a user, like calling it like a reference or a relation. Normally. I've called that in code, like a reference.

**Me:** And you either have a custom reference to a category or a native reference to a different ramp object.

**Me:** Yeah. Okay, so here we go. So they call them properties.

**Me:** And they've got some options here.

**Me:** They do have, like, person. I know. That's another thing, which is sort of. But they also have, like, relation. They've got like, roll up. They got all kinds of stuff going on. I do kind of like how specific they are about. We have text, we have number. Oh, that's where he got select from. Probably. And then multi select, which we could do from a database standpoint, like the architecture supports it, but also. But also, it's not. They do select is choose from a set of text options.

**Me:** That's what they have. Selection option or create one. So you've got.

**Me:** CEO. That's why he wanted to do it that way.

**Me:** Cfo.

**Me:** Oh, these are pages. That's so weird, as each row is a page, which kind of makes sense because, like, each of our custom and like, for each of our, like, custom rows or whatever for a job title, it's a page. And like, really, if, like, our. Our identity here is our user. Right. Our P keys. Our user. It's not a random thing in notion.

**Me:** Like it sort of does make sense from that standpoint.

**Me:** But, like, yeah, this is sort of a decent and I guess you can put colors on these and like, we could do this one day if we wanted to, but also, like, who gives a shit? Like, we're not notion. It doesn't need to be. Well, it's not quite as pretty. No, I don't care. Let's talk about the prettiness right now. More so, I'm thinking.

**Me:** Yeah.

**Me:** The difference, though, is I could never, like, refer. I'm not going to the CEO page and I'm seeing all the CEOs. That's the difference.

**Me:** Right. Sure. Yeah. Yeah. Because, like, even if you put, I mean.

**Me:** I don't know. I guess. Can you do, like, a filter? Can you filter for, like, filter by select is CEO?

**Me:** I guess you can. I guess if I change that to cfo.

**Me:** Well, yeah. Okay, so you do have some variant of, like, the filtering. And, like, this is a. But this is somehow a multi select, despite it being called a select.

**Me:** Well, it's a multi select will let you put. How do you. How do you have that change type? Oh, I changed it to multi select, I guess. Okay, so you can change the types a little bit here. What did I just do? I don't want to get too stuck on this feeling, but that. That makes. Sense, from the perspective of.

**Me:** I wonder what custom record yet for categories. Can I put add two categories? I can actually.

**Me:** In terms of, like, having different categories on the same object or, like, a multi select. Yeah, multi select for you. You could do multi select. I have mostly found so far that, like, it is not something people have actually really asked for. And as such, I'm like, fine, all right, let's keep it category it category. Seems fine to me. Go back.

**Me:** Cool. I select category.

**Me:** Yep.

**Me:** Now I need the option. Now I need the ability to pick one.

**Me:** You need the ability to say what those are. The beauty of doing the rows clear is then when you click the rows thing, the fact that it pops up like an empty table of rows and there's the. The type ahead and the hit enter or the plus. Exactly. Yeah, yeah, yeah, yep. Should I just use the component? That you were using before.

**Me:** The search. Which one?

**Me:** Because I could select.

**Me:** Which component are you thinking about here? Sorry? Are you thinking of, like, this guy, your local hosts?

**Me:** Yeah, this guy kind of like the table.

**Me:** I think we need something a little bit more lightweight. I agree. Yeah. For it. I think that, like, ideally, and this is probably a little bit of an aspiration, is like, if I select. Select here, whatever interface, I have to, like, add or remove them when I'm, like, before I've created the field at all.

**Me:** Should feel very similar to the interface once I've created it, and I want to manage those things.

**Me:** Right. Does that make sense?

**Me:** No, we see a visual example. So sort of my thought process is like, if this is what it looks like to manage my job titles, once I've created, like the concept of a job title and this is like my type management category, option management, this should feel as close as we can get it to when you're creating the thing. Like we should be reusing that code, reusing those components so that it feels intuitive. That's all I'm saying there. Walk me through me doing this. Today, a new category. Yeah. So today, how you do it is you literally will go over here and you go to users.

**Me:** And you'll be like. Or actually, no, you don't do it this way. Sorry. You say, I want to add a new field. I want to do.

**Me:** Favorite color.

**Me:** And then you create. And then you can upload a CSV or you can map from skim, or you can continue.

**Me:** This sort of wizard flow is not the greatest.

**Me:** We go to User. We've got a column for favorite color, and we say red.

**Me:** We create red, and now it shows up.

**Me:** And then I say oh, actually have the ability to just add options there Blue in which one? In the wizard. Just because I didn't. Okay. No, no reason beyond before, this was the only way that you assign stuff and you were always doing this like upsert semantic of like if you type something in we'll let you do it.

**Me:** But should we have in the drawer if you select? Because we. We need upload with CSV. We want to probably still keep the skin thing.

**Me:** I think you might draw my name. Yes. Would that be another? Because you can, like, make drawer steps. Yeah, you can do a little bit of that with drawers. It starts to, I think, feel a little bit annoying, but it's like, if you want it to feel like a guided flow inside it, if you select category, if. You put category. There's multiple steps here. Yep. I think that's fair. I think you just end up having to change this create button down here to be able.

**Me:** To be a next or whatever. Yeah, yeah. No, I think that's reasonable. I think that it's fair for it to be like, okay, there's a little bit more work you got to do here.

**Me:** But at the same time. But you want to nail the category experience. But if you're making a category, which is like, the main thing you're doing, you want to feel like you can sort of have all of that power immediately.

**Me:** Part of that is the bulk upload. Like, I had this case where this customer had whatever it was, 50 users in their initial business, and they had 200 job titles that they needed to do, like, spend programs and conditions and all kind of shit on before they invited everyone. And they're like, hey, Ethan, is there? A way for us to like, do this other than like uploading the first 50 in a CSV, attaching it to users, and then like replacing those values with a new set of 50.

**Me:** And I was like, sorry, y'all, there's not. And they were like, it's not a big deal. Like, they're resourceful. They. They knocked it out, they got it done. But, like, ideally, you can sort of bulk add all of them at once and not need them to be assigned to people in. Order to do that, but largely, like, the fact that that's not a thing yet is mostly just like, I was like, yeah, it's fine. This works. And not wanting to over index on, like, optimizing this experience because we're obviously building a much better one.

**Me:** But, yeah, I think if you're doing category, there's. There's a second page here, and it's. You need at least one category option. Maybe, like, maybe you even make that, like, a requirement of, like, you've got to put in at least one job title. You didn't get that before.

**Me:** Well, otherwise, you've got. And this is actually what the. What the UI deal is today is, like, you see in here, we got, like, favorite color. They don't have categories. They don't have color shot. Yeah. If there's no yeah, and maybe it's. That's possible.

**Me:** Yeah, I think that's fair, actually. I think that maybe it's just a. If this is empty, there's a CTA of some kind. If you're an admin who can go create these things? Yeah, sure. Hey, go add a new one.

**Me:** But, yeah, I think that. Yeah, I mean, I think that for that to be said, like, if we know that an admin is allowed to create new categories, maybe we just have a create button. Yeah, there's something we could take. You know how there's, like, the AI cell thing, we could probably put that, but. It's not AI. It's like, yeah, we can do. I mean, we can do what we did. What we did here, right? When I say yellow, I don't like this.

**Me:** You don't like this? No. Like you wouldn't want to just copy this and put it into the other one.

**Me:** I'm fine doing that. But you want something that's better than that.

**Me:** Well, it's like the problem is if go back to that. Yeah. Like this to me is I'm searching.

**Me:** Sure. Right. It doesn't make me feel like I'm adding a new option. Like if I actually go back to notion,

**Me:** Click on that.

**Me:** Oh, wow. They're the same way. That's. I was always weird. To me, I think that it's a. It's just a. It's just a minimum clicks thing. That's all it is, is. It's a, hey, if we know that you probably want this thing to exist and you're. Allowed to make it. Let's just give you a button that makes it cool. I agree that it is super intuitive, but fine, who cares? Great.

**Me:** Yeah, but, like, if I'm over here and I type yellow,

**Me:** There should be a button that will create yellow. Get back the ID having created yellow and then put yellow in there so that when I click Save changes it applies it.

**Me:** And if the side effect is if I change my mind In Yellow still exists as a category option out in the ether, that's fine. I don't think that's a big deal.

**Me:** Okay, let's talk CSV upload really quick.

**Me:** So I'm doing. I'm doing a category.

**Me:** I have to update on to the next page.

**Me:** All right, the code for this.

**Me:** You already done?

**Me:** I don't even know if that works. We'll do anything. I think it might be lying to us. Wait, you didn't give it a name, that's why.

**Me:** Let's do this.

**Me:** Let's do this.

**Me:** See what happens.

**Me:** Project field created.

**Me:** Did it actually do anything with the project field? Let's find out.

**Me:** Reload.

**Me:** I think I.

**Me:** Hope.

**Me:** D it.

**Me:** I think, regardless, like, that looks right to me. I think we should be showing.

**Me:** Well, that's because I have to. I have to unhide this.

**Me:** This is a super shitty ux.

**Me:** And I'm well aware no project says data found. Oops.

**Me:** Okay, so it just didn't work. It just broke. It didn't. Yeah. So, okay, the upload bit didn't work, but, like, the idea is there, right? It's like you've got an endpoint now that'll do that.

**Me:** I kind of like the idea of folding it into the actual create category endpoint just so that it's one request. Yeah, yeah, 100%. But, yeah, I mean, I think that, like, the only other knit I would have here is, like, if I upload it.

**Me:** I want to see what they are. Exactly. And sort of the. The nice way to do that is probably just inline them immediately into whatever the normal UI for. For the ad is. Right? Like if there's like a. If there's a button that I click and then I type in the name of a project and. I click like yes. And I would do that 20 times. If I upload a CSV with 20 rows, it should look the same as if I had done the 20 things manually.

**Me:** Yes. Right. It should feel the same. Third step in the drawer. I think that it's the same. It's a third step in this creation drawer, but it is the same. You're saying it's the same component as this? Yes, I think it's a similar component, and it's just in. This case, our component knows that its job is just to do shit later as opposed to if I'm editing stuff live. The components job is if I hit the trash can, it actually, like, deletes the thing.

**Me:** I give you the CSV, I hit the upload button. Yep. Go to the next page in the drawer. It's showing all the things that were taken from them. I would do here's. Here's kind of how I would do it is I would say,

**Me:** I'm on my page and it's job titles.

**Me:** Right? And then I've got a. How did I. Pajapulas is a new category I'm making. New category you're making. Yep. You're making a new category. I think. I think it's the same. So here's. So here's what I'm thinking we have is. We have, like, a big table that exists, and that's CEO.

**Me:** Product manager. And then there's a. There's a plus button right here.

**Me:** And then in addition to the plus button, there's a upload button right here. Got it. And if I click this upload button or I drag the CSV up to the upload button or whatever, it'll. It'll splat these out immediately. Yeah. And it'll just be like, okay, we did the work of typing all of these in for you, but we still got, like, the trashcan icons next to these or whatever.

**Me:** To remove them. And it's just if I've already created this category,

**Me:** Then the trash button is obviously much more consequential than if I'm setting it up for the first time.

**Me:** Okay. Okay. Does that. Yeah, I'm sure. Okay, so this is the second drawer in the creation. I've gotten this upload, so. So you've drawn it after I've entered stuff. But I'm thinking it's this. You're thinking what's sort of my landing? Yeah, sure. I. Still have job title. I just name that in this.

**Me:** And then the sort of descriptive text here is like, specify the valid job. There's nothing here. It's what you. It's a. It's that other thing you were showing. It's the go to custom data. Go back. You. Let's say you want to add where you had color, I guess.

**Me:** It's essentially a version of.

**Me:** Of. Of just for the job titles. Yeah, it's just like, one. It's sort of a one column table, and maybe there's a better component for a local column. There's, like, nothing here. It's just a list. Okay. Yep. All right, so I got like, blah, blah, blah. Start typing one in. I still have this plus, I guess you were saying the pluses. If I want to make one, I'm saying. Yeah, that's fine. Yeah, sold. But then there's this upload button over here. Yep. Bulk ad. Yeah, bulk ad. CSV, blah, blah, blah. Yeah, yeah. If I talk to this, you could even. Pop up zone. Yep, Sin. Exactly. I can cancel one if I want, with an X on the side.

**Me:** Or for removing one of these options. Yes, agreed. And then we're taking the exact same UX and it's just if you click that cancel button and you're creating the category for the first time, obviously that's not a big deal. It's not consequential. Once you've created it. And you have, oh, I have people whose favorite color is red and blue and yellow. And then you go and click the delete. We got to give you a confirm here. We got to be like, are you sure you want to delete this? And maybe it even says seven users have yet yellow is their favorite. Color. Yeah. Or whatever it is. And you can imagine seven users have yellow as their favorite color and 30 purchase orders have yellow is the associated color like you can imagine for deleting. I think that a single button that does a consequential delete is a bad idea.

**Me:** I think that it should be some amount of confirm, but my my sort of claim when you delete if anyone has.

**Me:** Options. I think maybe. Yeah, we can. We can sort of revisit that. I think it's probably sane for now, just as a. Don't worry about it. Too hard to be like, we're only showing it on this. Yeah, yeah. If you. If you're doing it as part of the sort of. Second drawer in this creation flow. It's not consequential yet. Just. Just remove it right once it exists and there is like rows, even if no one has it assigned. You could have a workflow that says if someone's favorite color is red, give them apples, even if no one has it assigned and like checking if every workflow uses this at all is is not feasible. So I think that it counts as consequential enough once it is like a real thing with a real id. Yeah, yeah, but if it doesn't have an ID associated with it yet, agree it's not real.

**Me:** On the CSV. You'll just send me back an error if there's something we can't. I think the CSV should be pretty. You can probably just do it from the front end. Like, I think there's probably enough front end logic to be able to just be like, hey, upload the CSV. My component's going to spit back a list of strings, turn that list of strings into a list.

**Me:** But what if, like, I'm making. Or are you saying making custom color and I give you a CSV with, like, 10 columns?

**Me:** Oh, I see what you're saying. That's a good question, I think. Let me look at what accounting does here, because accounting has this concept of, like, you have accounting fields.

**Me:** And, and this is the sort of UCSB thing, and I say add new field.

**Me:** And I say tasks here. And for them, they've got single select or text field. So maybe single select, but I like category more than single select. And then there's like, this template, and then you upload a completed template and I'm going to pull one in that I know is wrong. This is formatted. Wrong.

**Me:** And it just says missing required field name. Got it. Because they track it. But this is not using the fancy uploader that I normally use because for normal custom records stuff, it's like, there's so much complexity that, like, I don't know if I. How will you even know what colors is in? The CSV Favorite color.

**Me:** Yeah, I mean, I think that it's probably either a. It was usually like, when you. When I do this, other tools, you have to, like, map them. Yes. So that's what normally happens on a lot of other flows. So, like, I'm going to show you. That actually is like, this is the upload. Flow for, like, user job title.

**Me:** And if I do begin import here, it'll pop up. This is a third party thing called one schema. Why wouldn't I just use. What we use should be. Because this one lets you do a map and you say, I want to do upload and then you click confirm and then it's like, okay, what's your header row? And then you say, next. And then it's like, map your columns. So this is, like, sort of much more in depth.

**Me:** And there's a lot more power that comes with that, but also, it's like, much more of a pain in the ass.

**Me:** Totally. I agree.

**Me:** But. But I think maybe it's. I think it's probably like. I think it's totally sane for us to do something super dumb and be like, take the uploaded CSV, look at the first column and dedupe whatever's in it and just put it all in there.

**Me:** And if it's wrong, someone's going to look at it and they're going to be like, these are all my user emails. This is not what I actually wanted it to be. Yeah, these aren't my favorite colors.

**Me:** And then they we just need like a big bulk delete button on here. Actually, there needs to be like a clear button for clearing all of the options. That only shows up is the second step here.

**Me:** Does that make sense? Yeah. Yeah. It says if I. If I upload something wrong, but I think it can be a little bit.

**Me:** Yeah, I don't think it needs to be super polished.

**Me:** Yeah.

**Me:** But. Yeah, but I think that, like, roughly that. And then it's. And then after the second step, I finally can hit create.

**Me:** Yep. Boom, boom, boom, boom, boom, boom, boom. Come back to this people table. And then here. And then when I click on someone and I click edit profile. I should see it. It'll show up. Exactly. And it'll show me all of my options in these will all have, like, uuids. So part of the way that I've set this up is when you hit this patch endpoint to patch the user. If you're changing the job title, we don't send these strings, we send the ID of the row.

**Me:** And that way, like, if I'm a manager, I can't, like, send some random gobbledygook string.

**Me:** But that's where, like, the create has a second step to it. But, like, cool. But I think this. I think this makes sense. Does this. This makes sense. Does this resonate? Yeah. Okay. Yeah. Let's grab some pizza and then let's. Yeah, let's get to work. Sick. Let's do it.

**Me:** Yeah.

**Me:** Okay, cool.

**Me:** First thing is going to be.

**Me:** Going, Master. New branch. Pull the drawer in. I'm not thinking about the custom data tab.

**Me:** Yep. Not even think about it.

**Me:** Oh, boy.

**Me:** What's going on here?

**Me:** Two category.

**Me:** Text is fine. Just clean up that drawer bit.

**Me:** And then.

**Me:** Cool.

**Me:** Yeah, I might do the first part. The first, like, PR in the stack, I'm thinking doesn't have CSV upload for. Totally fine with that. Right? Yeah, I don't think it needs to be a. Yeah. And I think that, like, part of what sort of is nice is, like, if we do it. That way. What you can do is you can just have the first PR in the stack have, like a dummy feature flag on it. Exactly. And then once you merge the second one that has the CSV and it's like, okay, this is good and polished. We remove the dummy feature that we never turn on for anyone. Cool. But. Yeah, I mean, that's why I love. That's where I think graphite just comes. Oh, yeah. I mean, we were. We were. It was the most important thing with the ramp wrapped. Shit.
