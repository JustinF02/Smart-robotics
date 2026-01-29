// ##########################################################
//   _          _ _ _     
//  | |    __ _| (_) |__  
//  | |   / _` | | | '_ \ 
//  | |__| (_| | | | |_) |
//  |_____\__,_|_|_|_.__/ 
// ##########################################################

/*
  Place content at specified alignment with standard settings
*/
#let place_at(alignment, content) = {
  place(
    alignment,
    float: true,
    scope: "parent",
    clearance: 1em,
    content
  )
}

/*
  Quick emphasis text function for headers, labels, etc.
*/
#let emphasis_text(
  content,
  text_color: orange,
  text_style: "italic",
  text_weight: "bold",
  text_size: 1em,
) = {
  text(
    fill: text_color,
    style: text_style,
    weight: text_weight,
    size: text_size,
    content
  )
}

/*
  Insert special/annex page with customizable styling and content
*/
#let insert_annex_page(
  title: none,
  title_color: color.rgb("1f4e79"),
  title_size: 24pt,
  show_in_toc: false,
  label_name: none, // Label for the title using #link 
  page_break_before: true,
  page_break_after: false,
  content_alignment: center + top,
  column_count: none, // Number of columns for content layout
  content,
  gap_under_header: 1.5em,
) = {
  // Add page break before if requested
  if page_break_before {
    pagebreak()
  }

  // Local helper function to render title with consistent styling
  let render_title() = {
    if title == none { return }
    
    let title_content = text(size: title_size, weight: "bold", fill: title_color)[
      #title
      #if (label_name != none) { label(label_name) }
      ] 
    
    if show_in_toc {
      // Use heading to show in TOC with custom styling
      align(center + top)[
        #show heading: it => title_content
        #heading(level: 1, numbering: none)[#title]
      ]
      
    } else {
      // Use styled text (won't show in TOC)
      align(center + top)[#title_content]
    }

    v(gap_under_header)
  }
  
  // Render content with custom column layout
  if column_count != none {
    // Reset to single column temporarily
    set page(columns: 1)
    
    // Render title at full width
    render_title()
    
    // Apply multi-column layout to content
    columns(column_count)[
      #align(content_alignment)[#content]
    ]
  } else {
    // Single column or inherit current layout
    render_title()
    align(content_alignment)[#content]
  }
  
  // Add page break after if requested
  if page_break_after {
    pagebreak()
  }
}

/*
  Insert table of contents with customizable styling
*/
#let insert_toc(
  title: "Table of Contents",
  title_color: color.rgb("1f4e79"),
  title_size: 24pt,
  text_size: 11pt,
  max_depth: 3,
  indent: auto,
  page_break_before: true,
  page_break_after: true,
  show_in_toc: true,
) = {
  insert_annex_page(
    title: title,
    title_color: title_color,
    title_size: title_size,
    page_break_before: page_break_before,
    page_break_after: page_break_after,
    content_alignment: left + top,
    show_in_toc: show_in_toc,
    [
      // Generate the outline with custom text size
      #show outline.entry: it => {
        set text(size: text_size)
        it
      }
      
      #outline(
        title: none,
        depth: max_depth,
        indent: indent,
      )
    ]
  )
}

/*
  Create a heading that appears in TOC but is invisible on the page
*/
#let hidden_heading(
  title,
  level: 1,
  numbering: none,
) = {
  // Set up show rule to make this specific heading invisible
  show heading.where(body: [#title]): it => []
  // Create the heading (will be invisible due to show rule above)
  heading(level: level, numbering: numbering)[#title]
}
