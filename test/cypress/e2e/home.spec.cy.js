describe('home page spec', () => {
  it('contains the JB Logo', () => {
    cy.visit(Cypress.env('BASE_URL'))
    cy.screenshot('home', {capture: 'fullPage', scale: true, overwrite: true })
    cy.get('.logo').should('exist')
  })
})