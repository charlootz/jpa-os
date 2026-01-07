# Custom Records Eng Sync

**Date:** 2026-01-05
**Segments:** 141

---

## Transcript

**Me:** That's.

**Me:** What I put.

**Me:** I don't know.

**Me:** What that does. Okay, now you're recording. Yeah. Okay, cool.

**Me:** All right.

**Me:** Nice. Okay, cool. Yeah. So we can record this.

**Them:** We can record this, which will be good.

**Them:** But I guess really just to kick things off.

**Me:** Off. Super excited to have folks thinking about how we can build out a better customer experience. Custom record. We're getting shirts.

**Them:** Super excited to have folks thinking about how we can build out a better custom records experience. Custom records. We're getting shirts. I don't know where it's coming from, but I'm all about it. There's always money for. For merch. All is money for more merch.

**Me:** I don't know where that all about it. There's always money for merch there's always money from.

**Them:** So I guess, yeah, I am currently doing some work on some backend stuff to try to make categories a little bit easier to work with.

**Me:** Currently doing some work on some back end stuff to try to make categories a little bit easier to work with.

**Me:** I'm updating Recipe right now for creating a new custom category to accept a list of options.

**Them:** I'm updating the recipe right now for creating a new custom category Coleman to accept, like, a list of options.

**Them:** As just a list of strings, and so we can sort of create that to start with.

**Me:** As just a list of strings.

**Me:** And so.

**Me:** RT of create that to start with.

**Them:** I know, Julian. You've been doing some sort of refactoring work and trying to sort of attack what we have right now.

**Me:** I know, Julian. You've been doing some sort of accurate work. Time is over right now.

**Me:** Joe.

**Them:** Joe, I know you've been doing the creation for Primitives and then doing some work on the category creation and some of the management there, but I guess maybe the easiest way to get started is if one of you wants to just sort of go first and talk through what you've done. I know it's super early.

**Me:** Creation.

**Me:** Doing some work.

**Me:** On.

**Me:** The.

**Me:** Category creation.

**Me:** Management.

**Me:** But I guess maybe the easiest way.

**Me:** To get started.

**Me:** If one.

**Me:** Of you wants to just sort of go first and talk through what.

**Me:** I know.

**Them:** In terms of what you're thinking through and virtual. Julian, it's nice to meet you. Where are you from? How long you been at Ramp?

**Me:** Personal. Julian. It's nice to meet you. Where are you from? How long you been at Ramp?

**Them:** Based out of Denver. Nice to meet you as well. I've been here for gosh.

**Them:** May 12th was my start date. So when was that?

**Them:** By eight months ago, almost.

**Me:** Cool.

**Them:** Nine months.

**Them:** Seven months.

**Me:** I've been here. We're 63 days, 4 hours, 54 minutes and 34 seconds.

**Them:** I've been here for 63 days, 4 hours, 54 minutes and 34 seconds.

**Them:** That's fantastic. Nice.

**Me:** I'll tell you a little bit.

**Them:** I'll tell you a little bit about why I'm thinking about custom records.

**Me:** About why I'm thinking about custom records.

**Me:** And kind of how I'm trying to help.

**Them:** And kind of how I'm trying to help and I'm be curious just to hear your side.

**Me:** And I'd be curious.

**Me:** Just your.

**Me:** Side.

**Me:** So I'm this weirdo design engineer.

**Them:** So I'm this weirdo design engineer. I'm probably. The designers probably think I'm too engineer for them. Engineers probably think I'm too designy for them. So be it. That's. That's just how I am.

**Me:** Designers probably think I'm too engineering for them. Engineers designing for them.

**Me:** So be it. That's just how I am.

**Me:** I work on three projects. The one that takes up the most of my time is omnichat. And if you've seen some of that stuff,

**Them:** I work on three projects. The one that takes up most of my time is omnichat. I don't know if you've seen something on the chat stuff. It's one I'm, like, most excited and passionate about.

**Me:** Excited and passionate about. I think it could be the tip of our AI sphere.

**Them:** I think it could be the tip of our AI revenue sphere that, like, you know, familiarizes a lot of our customers with some AI products. The other product I work on is not quite ready yet, but have you seen the policy agents document editor?

**Me:** That familiarizes our customers with products.

**Me:** It's not quite ready yet. Have you seen the policy agents document?

**Them:** Yeah, you were working on that. Probably after Kat left.

**Me:** Yeah.

**Them:** Yeah, yeah. Some basically trying to build that team has already made one. I'm trying to basically build a more platform like version where other because in three months about three different teams are all going to have their own version of a document editor. Yay. I'm trying to basically build a component system that allows teams to build these plugins and stuff. And the third project is this. And the reason I'm kind of so excited about this is because for Omni, we have all this. This vision of all these grand things that the AI is going to be able to do for you. But the problem is, is our data is very. Much in a walled garden. And custom record says this ability to actually bring in stuff from the real world where your business actually happens and a lot of that product to be 10 times more valuable than than it currently is. So I've teamed up with Ethan here to get into the he's you're at. The ground? I don't know. Could you say I'm at the ground level? I feel like we're at the ground. I think we're all at the ground. We're out the ground level. Work around floor here to. To. To really like, basically because this product actually customers is pretty complex. Like, I. Think I record all of my conversations with Ethan purely so that I can have it translated to me as I kind of on board a little bit simpler. And I think that's actually the interesting thing here, right? It's like, got to get out of his brain, get all the teams to understand it, and eventually our customers. Right. So that's why I get really excited. This was initially pitched as a side project. It has become a main project. I actually kind of like that. It's just this small team and that's really how this gone. So my. My involvement has been pretty minimal to this point. The way we started, we had maybe too many, too much going on, and now we started to simplify it before the break, and so that's where we kind of are. And this PR that I put out earlier was basically a drawer that comes in, allows you to make custom records in line on the people tab. So we're very fresh. Very early. I'm very grateful that we actually have a professional front end engineer to rip rip my PR to shreds and teach me. So I meet you a similar boat. Yeah. So the thing that you had here it is live in qa. You can do the name. We've got some types here we've got Boolean text number don't have references here. We explicitly left that app. We chose not to do and then don't have categories here either. But we are also going to do a sort of a follow up. But I think the idea is like can we take this and say okay, if instead of text. I click category here and then I go to. We have some hand drawings that we are going to have Gemini.

**Me:** I'm basically trying to build that team has already made one. I'm trying to visit more platform like version or other. In three months about three different teams are all going to have version of Adoption editor. Yay. I'm trying to basically build a component system that allows you to build these plugins.

**Me:** And the third project is this.

**Me:** The reason I'm so excited about this is because for Omni, we have all.

**Me:** This vision of all these grand things.

**Me:** That the AI.

**Me:** Was from is our data.

**Me:** Is very much a.

**Me:** Wall garden.

**Me:** Custom records have this ability to actually bring in stuff from the real world.

**Me:** Business actually happens.

**Me:** 10 times more valuable.

**Me:** Than it currently.

**Me:** Is.

**Me:** You're at the ground.

**Me:** At the ground level.

**Me:** I feel like we're at the ground.

**Me:** We're out the ground level.

**Me:** Customer.

**Me:** I record all of my conversations.

**Me:** Ethan purely so that I can have it translated to me as I'm simpler. And I think that's actually.

**Me:** Going to get out of his rage. He used to understand.

**Me:** Our customers, right?

**Me:** So that's why I get really excited. This was initially pitched as a side project.

**Me:** It's become a main project.

**Me:** I actually kind of like that. It's just small team.

**Me:** And that's really how my development has been pretty minimal.

**Me:** To this point, the way we started, maybe too many going on, and now we start to simplify it. So that's where we kind of are. This PR that I put out earlier.

**Me:** Was basically a drawer that comes in, allows you to make custom records in line on tab. So we're very fresh, very early. I'm very grateful that we actually have a professional front engineer.

**Me:** To rip my prints and teach me.

**Me:** Nice to meet you. Similar bow, Yeah.

**Me:** So.

**Me:** Name.

**Me:** Types here.

**Me:** Don't have references here. We supposedly left it out.

**Me:** But I think the idea. Can we take say okay?

**Me:** If instead of text, I click category.

**Me:** And then I go. We have some hand drawings.

**Me:** Make turn wire frames and send chat later.

**Them:** Make, turn into wireframes and send to the chat later.

**Them:** Beautiful. Yeah. But then, Jason, Jen built out this sort of pretty nice. When you do this, you can go. And there's an option to, like, manage category values, really, I think something like this, but a little bit more polish, and I think we've got some room for here.

**Me:** When you do this.

**Me:** And.

**Me:** Go.

**Me:** Manage, worry about.

**Me:** Really?

**Me:** I think.

**Them:** In terms of adding the different options that show and then the editing stuff, obviously is sort of already ready to go for the people tab. I know you took over that pr, Julian.

**Me:** The editing stuff, obviously, is sort of already ready.

**Me:** Julian.

**Me:** I guess, turn a little bit.

**Them:** And so I guess, turning the floor over to you, I'd love to hear a little bit of what you're thinking about here.

**Me:** You're thinking.

**Me:** About where you.

**Them:** Where you sort of see things going.

**Me:** Everything else is on your eye.

**Them:** Everything else is that is on your mind.

**Them:** Yeah, definitely. Well, I think that we're all pretty aligned on this. It definitely sounds like we all have that.

**Them:** The goal of this being, like, a main project, I definitely like being too engineer, too designy at the same time.

**Them:** Yeah. Yeah, this. This is pretty.

**Them:** This is pretty much close to where I think I need to start. Like, really hitting the ground running is like finishing up this refactor. That's where I had previously left off. So simplifying the current custom records code, making sure that we produce, like, a really solid developer experience base. That way everybody can just kind of hit the ground running. I have some restacking magic that I need to get done, but I've since run into a lot of issues with our playwright Test suite is one of the main things that I'm trying to integrate is, like, as we're creating these features, as we're creating like these reusable components as we're thinking about not just Boolean text number.

**Them:** Or reference.

**Them:** But really sort of how we think about things in the grand scope.

**Them:** How we actually want to be writing these tests in a way that, like,

**Them:** Our engineers are going to go back and they're going to be able to reference these tests and say, like, well, how did they do things for the users? TABLE let's do the same thing for purchase orders. Let's do the same thing for.

**Me:** Yeah.

**Me:** Y.

**Me:** Eah.

**Them:** Everybody else. Right. And so making sure that we have a really solid component base there.

**Them:** Now there's the other side of things, which I think is even more exciting, which is like, actually building these things for other people, or at least like, giving people the tool set to do such a thing.

**Them:** So I have. I'm a little bit disjointed right now because I was just working on something else, but.

**Them:** Yeah. Also, I just, you know, two weeks, and I'm like, I have no memory of this place.

**Them:** Yeah. Next step would actually be the proof of concept for procurement. Ethan, you had brought this up kind of in our last conversation. I think about Friday, Thursday, last Thursday. I think that would. I think that would be worthwhile. I know procurement still pretty early on.

**Them:** They're sort of at the cusp of product market fit.

**Them:** And I think that having something like this.

**Them:** Makes a lot of sense, Joe. I think you and I have the same mind of, like, building a universal platform.
