<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class DashboardFacebookController extends AbstractController
{
    #[Route('/dashboard/facebook', name: 'app_dashboard_facebook')]
    public function index(): Response
    {

        $user = $this->getUser();
        return $this->render('dashboard_facebook/index.html.twig', [
            'username' => $user->getUsername()
        ]);
    }
}
