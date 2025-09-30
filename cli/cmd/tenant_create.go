package cmd

import (
	"errors"
	"fmt"

	"subnetter/internal/client"

	"github.com/spf13/cobra"
)

var tenantName string

var tenantCreateCmd = &cobra.Command{
	Use:   "create-tenant",
	Short: "Create a tenant",
	RunE: func(cmd *cobra.Command, args []string) error {
		if tenantName == "" {
			return errors.New("--name is required")
		}
		c := client.New(baseURL, idemKey)
		t, err := c.CreateTenant(tenantName)
		if err != nil {
			return err
		}
		fmt.Printf("Tenant created: %s  id=%s\n", t.Name, t.ID)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(tenantCreateCmd)
	tenantCreateCmd.Flags().StringVar(&tenantName, "name", "", "tenant name (required)")
}
