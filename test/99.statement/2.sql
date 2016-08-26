USE [eb_sales]
GO

/****** Object:  Table [dbo].[eb_issue]    Script Date: 2016/08/05 14:08:41 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[eb_issue](
	[id] [int] NOT NULL,
	[title] [nvarchar](30) NOT NULL,
	[content] [nvarchar](max) NOT NULL,
	[status] [nvarchar](1) NOT NULL,
	[created_date] [datetime] NOT NULL,
	[updated_date] [datetime] NOT NULL,
	[user_id] [int] NOT NULL,
	[deleted_date] [datetime] NULL,
	[is_deleted] [tinyint] NOT NULL,
	[end_date] [date] NULL,
	[level] [smallint] NOT NULL,
	[limit_date] [date] NULL,
	[resolve_user_id] [int] NULL,
	[solution] [nvarchar](max) NULL
)

GO


